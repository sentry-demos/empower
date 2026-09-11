"""Product search tool, backed by Flask GET /products."""

import json
import logging
from typing import Any

from agents import RunContextWrapper, function_tool

from ...session import ChatSession
from . import client

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# /products returns full descriptions and every review, which the model doesn't
# need and which would dominate the token budget. Keep the fields the chat
# product cards render, plus what flask /checkout reads back off cart['items'].
_PRODUCT_FIELDS = ("id", "title", "description", "price", "img", "imgcropped")

DEFAULT_LIMIT = 6


def trim_product(product: dict[str, Any]) -> dict[str, Any]:
    """Reduce a /products entry to the fields the chat flow actually uses."""
    return {key: product[key] for key in _PRODUCT_FIELDS if key in product}


@function_tool  # type: ignore[misc]
async def search_products(
    context: RunContextWrapper[ChatSession],
    max_price: float | None = None,
    query: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> str:
    """Search the Empower Plant catalogue.

    Args:
        max_price: Only return products at or below this price, in dollars.
        query: Optional text to match against product titles and descriptions.
        limit: Maximum number of products to return.

    Returns:
        JSON with the matching products.
    """
    session = context.context
    logging.debug(f"search_products max_price={max_price} query={query} limit={limit}")

    # Flask has no ?max_price=; filtering happens here so the backend needs no
    # change. ?fetch_promotions=true selects flask's extremely-slow profile,
    # which is what the agent_products_slow critical experience wants.
    params: dict[str, Any] = {}
    if "agent_products_slow" in client.outbound_headers().get("cexp", ""):
        params["fetch_promotions"] = "true"

    products = await client.get("/products", params=params)

    matches = [trim_product(product) for product in products]
    if max_price is not None:
        matches = [p for p in matches if p.get("price", 0) <= max_price]
    if query:
        needle = query.lower()
        matches = [
            p
            for p in matches
            if needle in p.get("title", "").lower()
            or needle in p.get("description", "").lower()
        ]

    matches = matches[: max(1, limit)]

    # Remember what was shown so add_to_cart can resolve an id back to the full
    # product without re-querying Flask.
    session.last_results = matches

    return json.dumps({"products": matches, "count": len(matches)})
