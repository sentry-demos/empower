"""Order status and cancellation tools, backed by Flask /orders.

Cancelling is the ghost tool failure in the demo. Flask's cancel endpoint marks
the order cancel_requested, then times out refunding it through the mock
payment provider and answers 500 — but the body still carries the order, and
cancel_order only looks at the body. So the model is handed an order that reads
as being cancelled, tells the customer so, and nothing on the agent side is
marked as failed: the only trace of the failure is the 500 on the http.client
span and the timeout under it in flask's own spans.

Unlike apply_coupon and purchase, this deliberately does not record a tool
error. That is the point being made — this one doesn't show up in Tool Errors.
"""

import json
import logging

from agents import RunContextWrapper, function_tool

from ...session import ChatSession
from . import client

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@function_tool  # type: ignore[misc]
async def get_order_status(
    context: RunContextWrapper[ChatSession], order_id: int
) -> str:
    """Look up an existing order.

    Args:
        order_id: The order number, e.g. 445 for "order #445".

    Returns:
        JSON with the order, or why it couldn't be found.
    """
    session = context.context
    logging.debug(f"get_order_status order_id={order_id}")

    status, body = await client.fetch(f"/orders/{order_id}")

    if status == 200:
        payload = {"ok": True, "order": body.get("order")}
    else:
        payload = {
            "ok": False,
            "order_id": order_id,
            "message": f"Order #{order_id} could not be found.",
        }
    session.record_widget("get_order_status", "order", payload)
    return json.dumps(payload)


@function_tool  # type: ignore[misc]
async def cancel_order(context: RunContextWrapper[ChatSession], order_id: int) -> str:
    """Cancel an existing order and refund the customer.

    Args:
        order_id: The order number, e.g. 445 for "order #445".

    Returns:
        JSON with the updated order.
    """
    session = context.context
    logging.debug(f"cancel_order order_id={order_id}")

    status, body = await client.post(f"/orders/{order_id}/cancel", {})

    if status == 404:
        payload = {
            "ok": False,
            "order_id": order_id,
            "message": f"Order #{order_id} could not be found.",
        }
    elif status == 409:
        payload = {
            "ok": False,
            "order": body.get("order"),
            "message": body["error"]["message"],
        }
    else:
        payload = {"ok": True, "order": body.get("order"), "refund": body.get("refund")}

    session.record_widget("cancel_order", "order", payload)
    return json.dumps(payload)
