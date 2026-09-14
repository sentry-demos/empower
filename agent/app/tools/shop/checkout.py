"""Coupon and purchase tools, backed by the real Flask checkout endpoints.

Both of these are expected to fail in the demo, and both already do with no new
backend code: SAVE20 is seeded expired so /apply-promo-code returns 410, and
/checkout with validate_inventory returns 500. The work here is reporting what
the backend actually said instead of flattening it into a generic error.
"""

import json
import logging

from agents import RunContextWrapper, function_tool

from ...session import DEFAULT_FORM, ChatSession
from . import client

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def _validate_inventory_flag() -> str:
    """Value to send for validate_inventory.

    A STRING, not a bool. flask/src/main.py compares it with
    `order["validate_inventory"] == "true"`, so a JSON boolean `true` compares
    False, skips validation and makes the purchase succeed — the opposite of the
    intended demo. CheckoutForm.jsx sends strings for the same reason.

    checkout_success is the healthy segment of the shared cexp schedule, so a
    nominal synthetic run buys successfully; standard_checkout_fail and a
    hand-driven demo (no cexp at all) both land on the 500.
    """
    cexp = client.outbound_headers().get("cexp", "")
    return "false" if "checkout_success" in cexp else "true"


@function_tool  # type: ignore[misc]
async def apply_coupon(context: RunContextWrapper[ChatSession], code: str) -> str:
    """Apply a promo code to the customer's order.

    Args:
        code: The promo code to apply, e.g. SAVE20.

    Returns:
        JSON describing whether the code was accepted, and why not if it wasn't.
    """
    session = context.context
    logging.debug(f"apply_coupon code={code}")

    status, body = await client.post("/apply-promo-code", {"value": code.strip()})

    if status == 200:
        session.promo = body.get("promo_code")
        payload = {"ok": True, "code": code, "promo": session.promo}
        session.record_widget("apply_coupon", "promo", payload)
        return json.dumps(payload)

    # Pass the backend's own wording through. The expired-coupon case is a 410
    # whose body explains itself; CheckoutForm.jsx throws that away and shows
    # "Unknown error applying promo code" instead.
    error = body.get("error") if isinstance(body, dict) else None
    payload = {
        "ok": False,
        "code": code,
        "status": status,
        "error_code": (error or {}).get("code", "error"),
        "message": (error or {}).get(
            "message", f"Could not apply {code} (HTTP {status})."
        ),
    }
    session.record_widget("apply_coupon", "promo", payload)
    return json.dumps(payload)


@function_tool  # type: ignore[misc]
async def purchase(context: RunContextWrapper[ChatSession]) -> str:
    """Place the order for everything in the customer's cart.

    Returns:
        JSON with the order result, or the error the backend returned.
    """
    session = context.context

    if not session.cart["items"]:
        payload = {"ok": False, "message": "The cart is empty."}
        session.record_widget("purchase", "confirmation", payload)
        return json.dumps(payload)

    form = session.form or dict(DEFAULT_FORM)
    validate_inventory = _validate_inventory_flag()
    logging.debug(f"purchase total={session.cart['total']} vi={validate_inventory}")

    status, body = await client.post(
        "/checkout",
        {
            "cart": session.cart,
            "form": form,
            "validate_inventory": validate_inventory,
        },
        # Mirrors CheckoutForm.jsx. Flask reads no `v2` param, but keeping it
        # means the chat and site checkouts are the same request.
        params={"v2": "true"},
    )

    if status == 200:
        order_total = session.cart["total"]
        item_count = sum(session.cart["quantities"].values())
        # Order placed: start the next conversation from an empty cart.
        session.cart = {"items": [], "quantities": {}, "total": 0}
        session.promo = None
        session.form = None
        payload = {
            "ok": True,
            "status": (body or {}).get("status", "success"),
            "order_total": order_total,
            "item_count": item_count,
        }
        session.record_widget("purchase", "confirmation", payload)
        return json.dumps(payload)

    payload = {
        "ok": False,
        "status": status,
        "message": f"Checkout failed (HTTP {status}).",
        "detail": body if isinstance(body, dict) else {"text": str(body)},
    }
    session.record_widget("purchase", "confirmation", payload)
    return json.dumps(payload)
