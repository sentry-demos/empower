"""A failing shopping tool has to fail its gen_ai.execute_tool span.

The expired coupon and the inventory 500 are the demo, and the tools report
them as ordinary JSON rather than raising — which means nothing marks the span
unless we do. These tests fail if someone drops that call, or if an SDK upgrade
changes which span is current inside a tool body: either way the Tool Errors
widget in Sentry would quietly go empty.
"""

import json
from typing import Any

import pytest
import sentry_sdk
from agents import RunContextWrapper
from sentry_sdk.consts import OP

from app.session import ChatSession
from app.tools.shop import apply_coupon
from app.tools.shop import client as shop_client
from app.tools.shop import purchase

TOOL_SPAN_NAME = "execute_tool under test"


def _events_client(events: list[Any]) -> sentry_sdk.Client:
    """A client whose transactions land in `events` instead of being sent."""

    def collect(event: Any, hint: Any) -> None:
        events.append(event)
        # Returning None drops the event, so nothing leaves the test.
        return None

    return sentry_sdk.Client(
        dsn="https://public@example.ingest.sentry.io/1",
        traces_sample_rate=1.0,
        before_send_transaction=collect,
    )


async def _run_in_tool_span(tool: Any, arguments: dict[str, Any], session: ChatSession):
    """Invoke `tool` the way the agents integration does, and return its span.

    The integration wraps on_invoke_tool in a gen_ai.execute_tool span; this
    stands in for that wrapper so the test exercises the real tool body.
    """
    events: list[Any] = []
    context = RunContextWrapper(session)

    with sentry_sdk.isolation_scope() as scope:
        scope.set_client(_events_client(events))
        with sentry_sdk.start_transaction(op="function", name="agent checkout_agent"):
            with sentry_sdk.start_span(op=OP.GEN_AI_EXECUTE_TOOL, name=TOOL_SPAN_NAME):
                result = await tool.on_invoke_tool(context, json.dumps(arguments))

    spans = [span for event in events for span in event["spans"]]
    tool_spans = [span for span in spans if span["description"] == TOOL_SPAN_NAME]
    assert len(tool_spans) == 1, spans
    return json.loads(result), tool_spans[0]


@pytest.mark.asyncio
async def test_rejected_coupon_fails_the_tool_span(monkeypatch):
    """SAVE20 is seeded expired, so /apply-promo-code answers 410."""

    async def expired(path, json_body, params=None):
        return 410, {"error": {"code": "promo-code-expired", "message": "expired"}}

    monkeypatch.setattr(shop_client, "post", expired)

    session = ChatSession("c1")
    payload, span = await _run_in_tool_span(apply_coupon, {"code": "SAVE20"}, session)

    assert payload["ok"] is False
    assert span["status"] == "internal_error"
    assert span["data"]["error.type"] == "apply_coupon.promo-code-expired"
    assert "410" in span["data"]["error.message"]

    # Handed up for ask_checkout_agent to fail the delegation span with.
    assert session.take_tool_error() == (
        span["data"]["error.type"],
        span["data"]["error.message"],
    )
    assert session.take_tool_error() is None, "a failure must only be marked once"


@pytest.mark.asyncio
async def test_failed_checkout_fails_the_tool_span(monkeypatch):
    """/checkout with validate_inventory returns 500."""

    async def broken(path, json_body, params=None):
        return 500, {"error": "inventory unavailable"}

    monkeypatch.setattr(shop_client, "post", broken)

    session = ChatSession("c2")
    session.add_items([{"id": 3, "title": "Plant Mood", "price": 155}], {3: 1})

    payload, span = await _run_in_tool_span(purchase, {}, session)

    assert payload["ok"] is False
    assert span["status"] == "internal_error"
    assert span["data"]["error.type"] == "purchase.http_500"
    assert "500" in span["data"]["error.message"]


@pytest.mark.asyncio
async def test_successful_checkout_leaves_the_tool_span_alone(monkeypatch):
    """The healthy path must stay out of the Tool Errors widget."""

    async def ok(path, json_body, params=None):
        return 200, {"status": "success"}

    monkeypatch.setattr(shop_client, "post", ok)

    session = ChatSession("c3")
    session.add_items([{"id": 3, "title": "Plant Mood", "price": 155}], {3: 1})

    payload, span = await _run_in_tool_span(purchase, {}, session)

    assert payload["ok"] is True
    assert span.get("status") != "internal_error"
    assert "error.type" not in (span.get("data") or {})
    assert session.take_tool_error() is None


def test_begin_turn_forgets_a_previous_turns_failure():
    """Otherwise the next delegation span inherits the last turn's error."""
    session = ChatSession("c4")
    session.tool_error = ("purchase.http_500", "Checkout failed (HTTP 500).")

    session.begin_turn()

    assert session.take_tool_error() is None
