"""The chatbot flow's application metrics: names, values and attributes."""

import json
from types import SimpleNamespace

import pytest
import sentry_sdk
from agents.stream_events import RunItemStreamEvent
from test_tool_errors import _run_in_tool_span

from app.api import chat_stream
from app.session import ChatSession
from app.tools.shop import client as shop_client
from app.tools.shop import search_policies, search_products
from app.tools.shop.policy_export import PAGE_COUNT


def _capture(monkeypatch):
    calls = []

    def distribution(name, value, **kwargs):
        calls.append((name, value, kwargs.get("attributes")))

    monkeypatch.setattr(sentry_sdk.metrics, "distribution", distribution)
    return calls


@pytest.mark.asyncio
async def test_policy_search_reports_documents_sent_to_the_model(monkeypatch):
    calls = _capture(monkeypatch)
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("m1")
    )

    assert (
        "agent.policy.documents",
        len(payload["pages"]),
        {"tool": "search_policies"},
    ) in calls
    # Unfixed behaviour: every page is sent.
    assert len(payload["pages"]) == PAGE_COUNT


@pytest.mark.asyncio
async def test_product_search_reports_result_count(monkeypatch):
    calls = _capture(monkeypatch)

    async def products(path, params=None):
        return [{"id": i, "title": f"Plant {i}", "price": 10} for i in range(4)]

    monkeypatch.setattr(shop_client, "get", products)
    payload, _ = await _run_in_tool_span(
        search_products, {"max_price": 200}, ChatSession("m2")
    )

    assert payload["count"] == 4
    assert ("agent.product_search.results", 4, {"tool": "search_products"}) in calls


@pytest.mark.asyncio
async def test_turn_reports_tool_call_count(monkeypatch):
    calls = _capture(monkeypatch)

    def tool_called(name, call_id):
        return RunItemStreamEvent(
            name="tool_called",
            item=SimpleNamespace(raw_item={"name": name, "call_id": call_id}),
        )

    class FakeResult:
        async def stream_events(self):
            yield tool_called("ask_checkout_agent", "c1")
            yield tool_called("ask_checkout_agent", "c2")

        def to_input_list(self):
            return []

    monkeypatch.setattr(
        chat_stream.Runner, "run_streamed", lambda *a, **k: FakeResult()
    )

    frames = [f async for f in chat_stream.stream_turn(ChatSession("m3"), "hi")]

    assert any("event: pills" in f for f in frames)
    assert (
        "agent.turn.tool_calls",
        2,
        {"agent": chat_stream.SHOPPING_AGENT_NAME},
    ) in calls
    assert json.loads(frames[-1].split("data: ")[1])["conversation_id"] == "m3"
