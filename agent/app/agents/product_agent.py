"""Product Agent — the catalogue specialist.

Owns everything to do with finding products. Invoked by shopping_agent as a
delegated sub-run, which is also what puts its spans in their own Sentry project
(see app/telemetry.py) — the agent boundary and the project boundary are the
same line.
"""

import logging

from agents import Agent, ModelSettings
from openai.types.shared import Reasoning

from config import settings

from ..tools.shop import search_products

# Configure logging
logging.basicConfig(level=logging.DEBUG)

PRODUCT_AGENT_NAME = "product_agent"
PRODUCT_AGENT_INSTRUCTIONS = """
You are the Empower Plant product specialist.

Your only job is looking things up in the catalogue with search_products.

- Translate the request into search_products arguments. "under $200" is
max_price=200; a description like "something for low light" is a query.
- Never invent products, prices or availability.

Call search_products once and stop. The orchestrator writes the reply to the
customer, so you do not need to summarise what you found.
"""

# Same constraint as the other agents: store=true is rejected here. See
# shopping_agent.py for why reasoning effort is pinned to "minimal".
#
# It matters most here: at the default, light_model (gpt-5-nano) spent ~830
# reasoning tokens on this one-tool decision and measured 8.1s, which is slower
# than the larger gpt-5-mini at 4.9s. Nano is cheaper per token, not faster. At
# "minimal" both land near 1.3s, so the model choice below is about cost again.
#
# tool_choice="required" pairs with tool_use_behavior below. Without it this
# agent sometimes answered in prose without searching at all, which showed up as
# "Show me plants under $200" returning no product card in 3.6s.
_model_settings = ModelSettings(
    store=False,
    reasoning=Reasoning(effort="minimal"),
    tool_choice="required",
)

product_agent = Agent(
    name=PRODUCT_AGENT_NAME,
    instructions=PRODUCT_AGENT_INSTRUCTIONS,
    # A narrow job over one tool — the cheaper model is enough, and this runs on
    # top of the orchestrator's own turn, so it is worth keeping light.
    model=settings.light_model,
    model_settings=_model_settings,
    tools=[search_products],
    # One search per delegation, and the raw result goes back to the
    # orchestrator. See checkout_agent.py for the full reasoning.
    tool_use_behavior="stop_on_first_tool",
)
