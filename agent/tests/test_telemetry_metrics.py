"""The shopping flow's application metrics are emitted with the right values."""

from types import SimpleNamespace

import pytest
import sentry_sdk
from agents.stream_events import RunItemStreamEvent
from test_tool_errors import _run_in_tool_span

from app.api import chat_stream
from app.session import ChatSession
from app.tools.shop import search_policies


@pytest.mark.asyncio
async def test_policy_documents_distribution_matches_pages_sent(monkeypatch):
    calls = []
    monkeypatch.setattr(
        sentry_sdk.metrics,
        "distribution",
        lambda name, value, **kw: calls.append((name, value, kw)),
    )

    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("m1")
    )

    assert calls == [
        (
            "agent.policy.documents",
            len(payload["pages"]),
            {"attributes": {"tool": "search_policies"}},
        )
    ]


@pytest.mark.asyncio
async def test_turn_tool_calls_distribution(monkeypatch):
    calls = []
    monkeypatch.setattr(
        sentry_sdk.metrics,
        "distribution",
        lambda name, value, **kw: calls.append((name, value, kw)),
    )

    def tool_called(call_id):
        item = SimpleNamespace(raw_item={"name": "ask_checkout_agent", "call_id": call_id})
        return RunItemStreamEvent(name="tool_called", item=item)

    class FakeResult:
        async def stream_events(self):
            yield tool_called("c1")
            yield tool_called("c2")

        def to_input_list(self):
            return []

    monkeypatch.setattr(
        chat_stream.Runner, "run_streamed", lambda *a, **k: FakeResult()
    )

    frames = [f async for f in chat_stream.stream_turn(ChatSession("m2"), "hi")]

    assert frames[-1].startswith("event: done")
    assert (
        "agent.turn.tool_calls",
        2,
        {"attributes": {"agent": "manager"}},
    ) in calls
