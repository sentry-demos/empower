"""Cart and checkout-form tools. These mutate the agent's own session only.

The chat cart is deliberately separate from the site's Redux cart: the point of
the demo is that tool calls change real server-side state, which is what shows
up in the trace. It is kept in the shape react/src/reducers/index.js produces so
Flask's /checkout accepts it verbatim from either flow.
"""

import json
import logging
from typing import Any

from agents import RunContextWrapper, function_tool
from pydantic import BaseModel

from ...session import DEFAULT_FORM, ChatSession
from ...telemetry import shopping_client, tool_span
from . import client
from .search_products import trim_product

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class CartLine(BaseModel):
    """One requested line item.

    A model rather than a plain dict: the SDK generates a strict JSON schema for
    tool params, and dict[str, int] emits `additionalProperties`, which strict
    mode rejects outright at import time.
    """

    product_id: int
    qty: int = 1


async def _resolve_products(
    session: ChatSession, product_ids: list[int]
) -> dict[int, dict[str, Any]]:
    """Look up full products for the given ids.

    Prefers whatever search_products last showed, so the common path costs no
    extra Flask call, and falls back to /products when the model names something
    that wasn't in the last result set.
    """
    known = {product["id"]: product for product in session.last_results}
    missing = [pid for pid in product_ids if pid not in known]

    if missing:
        for product in await client.get("/products"):
            if product["id"] in missing:
                known[product["id"]] = trim_product(product)

    return known


@function_tool  # type: ignore[misc]
async def add_to_cart(
    context: RunContextWrapper[ChatSession], items: list[CartLine]
) -> str:
    """Add one or more products to the customer's cart.

    Args:
        items: Products to add, each with a product_id and a qty.

    Returns:
        JSON with the updated cart.
    """
    session = context.context
    logging.debug(f"add_to_cart items={items}")

    requested: dict[int, int] = {}
    for item in items:
        requested[item.product_id] = requested.get(item.product_id, 0) + max(
            1, item.qty
        )

    # Cart and checkout work reports to its own Sentry project.
    with tool_span(shopping_client(), "add_to_cart"):
        resolved = await _resolve_products(session, list(requested))

        unknown = [pid for pid in requested if pid not in resolved]
        products = [resolved[pid] for pid in requested if pid in resolved]
        quantities = {pid: qty for pid, qty in requested.items() if pid in resolved}

        session.add_items(products, quantities)

    return json.dumps(
        {
            "cart": session.cart,
            "added": [
                {"product_id": pid, "qty": qty} for pid, qty in quantities.items()
            ],
            "unknown_product_ids": unknown,
        }
    )


@function_tool  # type: ignore[misc]
async def view_cart(context: RunContextWrapper[ChatSession]) -> str:
    """Show what is currently in the customer's cart.

    Returns:
        JSON with the cart contents.
    """
    session = context.context
    logging.debug(f"view_cart total={session.cart['total']}")
    with tool_span(shopping_client(), "view_cart"):
        return json.dumps({"cart": session.cart, "promo": session.promo})


@function_tool  # type: ignore[misc]
async def start_checkout(context: RunContextWrapper[ChatSession]) -> str:
    """Begin checkout and return the prefilled checkout form.

    Returns:
        JSON with the cart and the prefilled form.
    """
    session = context.context

    if not session.cart["items"]:
        return json.dumps({"error": "The cart is empty; add something first."})

    # Prefilled the same way CheckoutForm.jsx does, so the chat checkout and the
    # site checkout show the customer the same defaults.
    if session.form is None:
        session.form = dict(DEFAULT_FORM)

    logging.debug(f"start_checkout total={session.cart['total']}")
    with tool_span(shopping_client(), "start_checkout"):
        return json.dumps(
            {"cart": session.cart, "form": session.form, "promo": session.promo}
        )
