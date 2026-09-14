"""Shopping Agent — the orchestrator behind the chat widget.

Three agents, one per area of the flow:

    shopping_agent  this file   routes the conversation
    product_agent               the catalogue
    checkout_agent              cart, coupon, order

The sub-agents are delegated to as tools rather than handed off to. A handoff
transfers control — the conversation would move to checkout_agent and stay there
— which does not suit a flow that alternates between browsing and buying. A
delegated sub-run also gives us a place to bind a different Sentry client, so
each agent's spans land in its own project; a handoff's spans are children of
the caller's transaction and cannot be routed anywhere.

Separate from manager_agent, which keeps driving the scripted /buy-plants flow.
"""

import logging

from agents import Agent, ModelSettings, RunContextWrapper, Runner, function_tool
from openai.types.shared import Reasoning

from config import settings

from ..session import ChatSession
from ..telemetry import agent_transaction, plant_client, shopping_client
from .checkout_agent import checkout_agent
from .plant_expert_agent import plant_expert_agent
from .product_agent import product_agent

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def _checkout_context(session: ChatSession) -> str:
    """Facts the checkout specialist needs but cannot otherwise know.

    A delegated sub-run starts cold: it sees the request string and nothing
    else. Without this it cannot act on "add one of each" (it has no product
    ids) or "apply the coupon" (it has no code), because that context lives in
    the orchestrator's conversation, not in its own.
    """
    lines = []

    if session.last_results:
        shown = ", ".join(
            f"{p['title']} (id {p['id']}, ${p['price']})" for p in session.last_results
        )
        lines.append(f"Products currently shown to the customer: {shown}.")

    if session.cart["items"]:
        items = ", ".join(
            f"{item['title']} (id {item['id']}) x"
            f"{session.cart['quantities'].get(str(item['id']), 0)}"
            for item in session.cart["items"]
        )
        lines.append(f"Cart contains: {items}. Total ${session.cart['total']}.")
    else:
        lines.append("The cart is empty.")

    if session.form and session.form.get("promoCode"):
        lines.append(
            f"Promo code on the checkout form: {session.form['promoCode']}."
        )

    return "\n".join(lines)


# Returned instead of running a specialist a second time in one turn. Phrased as
# an instruction because it lands in the model's context as a tool result: the
# useful next move is to reply, not to try another specialist.
_ALREADY_DELEGATED = (
    "You have already called a specialist for this message and the customer can"
    " see the result. Do not call another specialist. Reply to the customer now,"
    " in one short sentence, and let them say what they want next."
)


@function_tool  # type: ignore[misc]
async def ask_product_agent(
    context: RunContextWrapper[ChatSession], request: str
) -> str:
    """Ask the product specialist to find products in the catalogue.

    Args:
        request: What the customer is looking for, in plain language.

    Returns:
        What the product specialist found.
    """
    session = context.context
    if not session.claim_delegation("product_agent"):
        logging.debug("refusing second delegation this turn (product_agent)")
        return _ALREADY_DELEGATED

    logging.debug(f"delegating to product_agent: {request}")
    with agent_transaction(plant_client(), "product_agent"):
        result = await Runner.run(product_agent, request, context=session)
    return str(result.final_output)


@function_tool  # type: ignore[misc]
async def ask_checkout_agent(
    context: RunContextWrapper[ChatSession], request: str
) -> str:
    """Ask the checkout specialist to work on the cart or the order.

    Args:
        request: What to do — add to cart, show the cart, start checkout, apply a
            coupon, or place the order.

    Returns:
        What the checkout specialist did.
    """
    session = context.context
    if not session.claim_delegation("checkout_agent"):
        logging.debug("refusing second delegation this turn (checkout_agent)")
        return _ALREADY_DELEGATED

    logging.debug(f"delegating to checkout_agent: {request}")
    briefed = f"{_checkout_context(session)}\n\nRequest: {request}"
    with agent_transaction(shopping_client(), "checkout_agent"):
        result = await Runner.run(checkout_agent, briefed, context=session)
    return str(result.final_output)


SHOPPING_AGENT_NAME = "shopping_agent"
SHOPPING_AGENT_INSTRUCTIONS = """
You are the Empower Plant shopping assistant, talking to a customer in a chat
widget on the storefront. You do not do the work yourself — you route it:

1. Anything about what is available, finding or searching products: call
ask_product_agent with what the customer wants.
2. Anything about the cart, the checkout form, a promo code, or placing the
order: call ask_checkout_agent, saying which of those to do.
3. Plant care questions rather than shopping: hand off to the Plant Expert
Agent.

Rules:

- Call exactly ONE specialist per customer message, exactly once, then reply.
Never call both. Never call one and then the other. After a specialist returns,
your next output is your reply to the customer — not another tool call. If the
customer wants something else afterwards, they will ask.
- Never chain a purchase onto anything else — if a coupon fails, say so and ask.
- Only ask the checkout specialist to place the order when the customer
explicitly asked to buy, purchase or place the order.
- Do not ask for confirmation before searching, adding to the cart or starting
checkout; the customer already asked.
- Keep replies to one short sentence. The chat renders products, the cart, the
checkout form and errors as cards, so never list them out or repeat prices.
- Never ask the customer for payment details; the checkout form is prefilled.
"""

# Same constraint as the other agents: store=true is rejected here.
#
# reasoning effort "minimal" is load-bearing for the chat's responsiveness. At
# the gpt-5 default this model spends ~190 reasoning tokens deciding which
# specialist to call, which measured 5.7s per call against 1.5s at "minimal" —
# and a turn is four sequential calls (orchestrator routes, sub-agent picks a
# tool, sub-agent summarises, orchestrator replies), so the default put
# cart/checkout turns at 11-18s with no backend call in them at all. "low" is
# not a middle ground: it still spends the full reasoning budget. Routing to one
# of two tools needs no deliberation, so nothing is lost.
_model_settings = ModelSettings(store=False, reasoning=Reasoning(effort="minimal"))

_HAND_BACK = (
    "Once you have provided the recommendations, handoff the task\n"
    "back to the Manager Agent."
)
_ANSWER_DIRECTLY = (
    "Answer the customer directly and keep it to two or three sentences."
    " Do not hand the conversation back to another agent."
)

if _HAND_BACK not in plant_expert_agent.instructions:
    # Fail loudly rather than silently shipping an expert that hands the turn
    # back and swallows its own answer.
    raise RuntimeError(
        "plant_expert_agent instructions changed; update _HAND_BACK in "
        "shopping_agent.py to match."
    )

# plant_expert_agent is a module-level singleton, and importing manager_agent
# mutates its .handoffs to point back at manager_agent. Handing off to it
# directly would drop the customer into the /buy-plants workflow mid-chat, so
# clone it for this flow.
#
# The clone also stops handing the turn back. The original hands control to
# whoever called it once it has recommendations, which in a chat means the
# expert's answer is never what the turn ends on — the customer sees only
# "handing you off to our plant expert" and then nothing. Here the expert is
# the last agent to speak, so its answer is the reply.
shopping_plant_expert = plant_expert_agent.clone(
    instructions=plant_expert_agent.instructions.replace(
        _HAND_BACK, _ANSWER_DIRECTLY
    ),
    handoffs=[],
)

# Create the shopping agent
shopping_agent = Agent(
    name=SHOPPING_AGENT_NAME,
    instructions=SHOPPING_AGENT_INSTRUCTIONS,
    model=settings.agent_model,
    model_settings=_model_settings,
    tools=[ask_product_agent, ask_checkout_agent],
)

shopping_agent.handoffs = [shopping_plant_expert]
