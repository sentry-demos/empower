"""Product Agent — the catalogue specialist.

Owns everything to do with finding products. Invoked by shopping_agent as a
delegated sub-run, which is also what puts its spans in their own Sentry project
(see app/telemetry.py) — the agent boundary and the project boundary are the
same line.
"""

import logging

from agents import Agent, ModelSettings

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
- Never invent products, prices or availability. If nothing matches, say so.
- Reply with one short sentence naming what you found. The chat renders the
products as cards, so do not list them out or repeat prices.
"""

# Same constraint as the other agents: store=true is rejected here.
_model_settings = ModelSettings(store=False)

product_agent = Agent(
    name=PRODUCT_AGENT_NAME,
    instructions=PRODUCT_AGENT_INSTRUCTIONS,
    # A narrow job over one tool — the cheaper model is enough, and this runs on
    # top of the orchestrator's own turn, so it is worth keeping light.
    model=settings.light_model,
    model_settings=_model_settings,
    tools=[search_products],
)
