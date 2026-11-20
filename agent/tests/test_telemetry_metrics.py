"""The application metrics that follow the chatbot flow stage by stage."""

import pytest
import sentry_sdk
from test_tool_errors import _run_in_tool_span

from app.api import chat_stream
from app.session import ChatSession
from app.tools.shop import client, search_policies, search_products
from app.tools.shop.policy_export import PAGE_COUNT


@pytest.fixture
def distributions(monkeypatch):
    calls = []

    def record(name, value, **kwargs):
        calls.append((name, value, kwargs.get("attributes")))

    monkeypatch.setattr(sentry_sdk.metrics, "distribution", record)
    return calls


@pytest.mark.asyncio
async def test_policy_search_reports_documents_sent_to_the_model(distributions):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("m1")
    )

    # Pinned to the current behaviour: every page of the export goes out.
    assert (
        "agent.policy.documents",
        len(payload["pages"]),
        {"tool": "search_policies"},
    ) in distributions
    assert len(payload["pages"]) == PAGE_COUNT


@pytest.mark.asyncio
async def test_product_search_reports_result_count(monkeypatch, distributions):
    async def fake_get(path, params=None):
        return [
            {"id": i, "title": f"Plant {i}", "price": 10 * i} for i in range(1, 5)
        ]

    monkeypatch.setattr(client, "get", fake_get)
    monkeypatch.setattr(client, "outbound_headers", lambda: {})

    payload, _ = await _run_in_tool_span(
        search_products, {"max_price": 25}, ChatSession("m2")
    )

    assert payload["count"] == 2
    assert (
        "agent.products.results",
        2,
        {"tool": "search_products"},
    ) in distributions


@pytest.mark.asyncio
async def test_turn_reports_tool_call_count(monkeypatch, distributions):
    class FakeResult:
        async def stream_events(self):
            for _ in ():
                yield _

        def to_input_list(self):
            return []

    monkeypatch.setattr(
        chat_stream.Runner, "run_streamed", lambda *a, **k: FakeResult()
    )

    frames = [f async for f in chat_stream.stream_turn(ChatSession("m3"), "hi")]

    assert any("event: done" in f for f in frames)
    assert (
        "agent.turn.tool_calls",
        0,
        {"agent": chat_stream.SHOPPING_AGENT_NAME},
    ) in distributions
