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

You handle the cart and the order:

- add_to_cart takes product ids. "One of each" means quantity 1 of every product
the customer was just shown.
- view_cart shows the cart, start_checkout returns the prefilled form.
- apply_coupon applies a promo code. purchase places the order.
- Do exactly the one thing you were asked for. Never place the order unless you
were explicitly asked to buy, and never place it just because a coupon failed.
- If a tool reports a failure, say what the backend said. Do not retry it and do
not soften it — the error message is the useful part.

Reply with one short sentence. The chat renders the cart, checkout form and
errors as cards, so do not repeat their contents in prose.
"""

# Same constraint as the other agents: store=true is rejected here. See
# shopping_agent.py for why reasoning effort is pinned to "minimal" — this agent
# contributes two of the four LLM calls in a cart or checkout turn, and its
# tools are pure session mutations with no network call to hide behind.
_model_settings = ModelSettings(store=False, reasoning=Reasoning(effort="minimal"))

checkout_agent = Agent(
    name=CHECKOUT_AGENT_NAME,
    instructions=CHECKOUT_AGENT_INSTRUCTIONS,
    model=settings.agent_model,
    model_settings=_model_settings,
    tools=[add_to_cart, view_cart, start_checkout, apply_coupon, purchase],
)
