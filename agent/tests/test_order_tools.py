"""The stock check and order tools, against a stubbed Flask.

cancel_order is the ghost tool failure: Flask answers 500 after the refund
times out, and the tool must keep reporting that as a cancelled order without
failing its span. If someone "fixes" either half, the demo stops showing what it
is meant to, so these tests pin the broken behaviour down on purpose.
"""

import json

import pytest
from agents import RunContextWrapper
from test_tool_errors import _run_in_tool_span

from app.session import ChatSession
from app.tools.shop import cancel_order, check_inventory
from app.tools.shop import client as shop_client
from app.tools.shop import get_order_status

ORDER = {"id": 445, "status": "processing", "total": 485, "items": "1 x Plant Mood"}


async def _invoke(tool, arguments, session):
    result = await tool.on_invoke_tool(
        RunContextWrapper(session), json.dumps(arguments)
    )
    return json.loads(result)


@pytest.mark.asyncio
async def test_check_inventory_reports_stock_and_renders_a_card(monkeypatch):
    seen = {}

    async def stock(path, params=None):
        seen.update(path=path, params=params)
        return {
            "products": [{"id": 3, "title": "Plant Mood", "count": 1, "in_stock": True}]
        }

    monkeypatch.setattr(shop_client, "get", stock)

    session = ChatSession("s1")
    payload = await _invoke(check_inventory, {"product": " Plant Mood "}, session)

    assert seen == {"path": "/inventory", "params": {"product": "Plant Mood"}}
    assert payload["products"][0]["in_stock"] is True
    assert session.drain_widgets() == [
        {"type": "inventory", "tool": "check_inventory", "data": payload}
    ]


@pytest.mark.asyncio
async def test_unknown_order_is_reported_as_not_found(monkeypatch):
    async def missing(path, params=None):
        return 404, {"error": {"code": "not_found", "message": "Order not found."}}

    monkeypatch.setattr(shop_client, "fetch", missing)

    payload = await _invoke(get_order_status, {"order_id": 999}, ChatSession("s2"))

    assert payload["ok"] is False
    assert "999" in payload["message"]


@pytest.mark.asyncio
async def test_shipped_order_cannot_be_cancelled(monkeypatch):
    async def shipped(path, json_body, params=None):
        return 409, {
            "error": {
                "code": "not_cancellable",
                "message": "Order has already been shipped.",
            },
            "order": {**ORDER, "id": 444, "status": "shipped"},
        }

    monkeypatch.setattr(shop_client, "post", shipped)

    payload = await _invoke(cancel_order, {"order_id": 444}, ChatSession("s3"))

    assert payload["ok"] is False
    assert payload["message"] == "Order has already been shipped."


@pytest.mark.asyncio
async def test_refund_timeout_is_reported_as_a_cancellation(monkeypatch):
    """The ghost failure: a 500 that reaches the model looking like success."""
    calls = []

    async def timed_out(path, json_body, params=None):
        calls.append(path)
        return 500, {
            "order": {**ORDER, "status": "cancel_requested"},
            "refund": None,
            "error": {
                "code": "payment_provider_timeout",
                "message": "Refund was not confirmed.",
            },
        }

    monkeypatch.setattr(shop_client, "post", timed_out)

    session = ChatSession("s4")
    payload, span = await _run_in_tool_span(cancel_order, {"order_id": 445}, session)

    assert calls == ["/orders/445/cancel"]
    # Searchable in Trace Explorer by the order the customer asked about.
    assert span["data"]["order.id"] == 445
    assert payload["ok"] is True
    assert payload["order"]["status"] == "cancel_requested"
    assert "error" not in payload

    # Invisible to Tool Errors: neither this span nor the delegation is failed.
    assert span.get("status") != "internal_error"
    assert "error.type" not in (span.get("data") or {})
    assert session.take_tool_error() is None


def test_agent_logs_are_sent_to_sentry():
    """The tools' INFO lines are what put the 500 next to the green tool span."""
    from app.telemetry import sentry_options

    assert sentry_options("")["enable_logs"] is True
