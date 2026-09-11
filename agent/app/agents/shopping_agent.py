"""Shopping Agent backing the conversational storefront in the chat widget.

Separate from manager_agent, which keeps driving the scripted /buy-plants flow.
This one runs a real LLM loop over the user's own messages, with tools that hit
the Flask backend.
"""

import logging

from agents import Agent, ModelSettings

from config import settings

from ..tools.shop import search_products
from .plant_expert_agent import plant_expert_agent

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Shopping agent configuration
SHOPPING_AGENT_NAME = "shopping_agent"
SHOPPING_AGENT_INSTRUCTIONS = """
You are the Empower Plant shopping assistant, talking to a customer in a chat
widget on the storefront.

Help the customer find products, add them to their cart, and check out:

1. Use search_products to look up the catalogue whenever the customer asks what
is available or describes what they want. Never invent products or prices.
2. Keep replies short — one or two sentences. The chat renders the products,
cart and checkout form as cards, so do not list them out in prose or repeat
prices and descriptions the cards already show.
3. If the customer asks about plant care rather than shopping, hand off to the
Plant Expert Agent.

Do not ask for confirmation before searching. Never ask the customer for
payment details; the checkout form is prefilled.
"""

# Same constraint as the other agents: store=true is rejected here.
_model_settings = ModelSettings(store=False)

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
    tools=[search_products],
)

shopping_agent.handoffs = [shopping_plant_expert]
