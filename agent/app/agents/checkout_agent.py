"""Checkout Agent — the cart and order specialist.

Owns the cart, the checkout form, coupons and placing the order. Invoked by
shopping_agent as a delegated sub-run, which is also what puts its spans in
their own Sentry project (see app/telemetry.py).
"""

import logging

from agents import Agent, ModelSettings
from openai.types.shared import Reasoning

from config import settings

from ..tools.shop import (
    add_to_cart,
    apply_coupon,
    purchase,
    start_checkout,
    view_cart,
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

CHECKOUT_AGENT_NAME = "checkout_agent"
CHECKOUT_AGENT_INSTRUCTIONS = """
You are the Empower Plant checkout specialist.

You handle the cart and the order. Call exactly ONE tool — the single tool that
does what you were asked, and nothing more:

- add_to_cart takes product ids. "One of each" means quantity 1 of every product
the customer was just shown.
- view_cart shows the cart, start_checkout returns the prefilled form.
- apply_coupon applies a promo code. purchase places the order.

Starting checkout is not applying a coupon, and neither one is buying. A promo
code appearing on the checkout form is not a request to apply it. Only apply a
coupon when asked for a coupon, and only place the order when asked to buy.
"""

# Same constraint as the other agents: store=true is rejected here. See
# shopping_agent.py for why reasoning effort is pinned to "minimal" — this agent
# contributes two of the four LLM calls in a cart or checkout turn, and its
# tools are pure session mutations with no network call to hide behind.
#
# tool_choice="required" pairs with tool_use_behavior below: the model must call
# a tool, and the run stops after the first one.
_model_settings = ModelSettings(
    store=False,
    reasoning=Reasoning(effort="minimal"),
    tool_choice="required",
)

checkout_agent = Agent(
    name=CHECKOUT_AGENT_NAME,
    instructions=CHECKOUT_AGENT_INSTRUCTIONS,
    model=settings.agent_model,
    model_settings=_model_settings,
    tools=[add_to_cart, view_cart, start_checkout, apply_coupon, purchase],
    # Exactly one tool call per delegation, enforced rather than asked for.
    #
    # This agent holds all five shopping tools, and by default the SDK loops
    # until the model stops calling them — so one "Purchase" message was
    # observed running a cart op, start_checkout, apply_coupon AND purchase in a
    # single delegation, four cards deep. Conversely, at minimal reasoning effort
    # the model sometimes answered in prose without calling anything, leaving the
    # customer with no card at all (4 of 20 turns).
    #
    # tool_choice guarantees something runs; stop_on_first_tool guarantees only
    # one thing runs and makes its JSON the result the orchestrator sees. The
    # orchestrator writes the customer-facing sentence, so this also removes this
    # agent's summarising round-trip.
    #
    # Cost: a single message asking for two things ("add these and check out")
    # now does only the first. That is the intended trade — every action has to
    # be something the customer explicitly asked for.
    tool_use_behavior="stop_on_first_tool",
)
