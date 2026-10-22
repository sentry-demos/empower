"""Stock check tool, backed by Flask GET /inventory.

Slow by design, and not because of the model: /inventory reads from
warehouse_stock, a legacy unindexed view that takes ~20s on its own (see
_postgres/data/orders.sql). The LLM calls on either side of it take a couple of
seconds between them, so the trace is what settles where a slow "is this in
stock?" turn actually spent its time.
"""

import json
import logging

from agents import RunContextWrapper, function_tool

from ...session import ChatSession
from . import client

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@function_tool  # type: ignore[misc]
async def check_inventory(context: RunContextWrapper[ChatSession], product: str) -> str:
    """Check how many units of a product are in stock.

    Args:
        product: The product name, or part of it, e.g. "Plant Mood".

    Returns:
        JSON with each matching product and its stock count.
    """
    session = context.context
    logging.debug(f"check_inventory product={product}")

    body = await client.get("/inventory", params={"product": product.strip()})

    payload = {"product": product, "products": body.get("products", [])}
    session.record_widget("check_inventory", "inventory", payload)
    return json.dumps(payload)
