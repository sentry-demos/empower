"""Application metrics for the chat flow: what is emitted, with which values."""

from types import SimpleNamespace

import pytest
import sentry_sdk
from agents.stream_events import RunItemStreamEvent
from test_tool_errors import _run_in_tool_span

from app.api import chat_stream
from app.session import ChatSession
from app.tools.shop import search_policies


def _record(monkeypatch, kind):
    calls = []
    monkeypatch.setattr(
        sentry_sdk.metrics,
        kind,
        lambda name, value, **kwargs: calls.append((name, value, kwargs)),
    )
    return calls


@pytest.mark.asyncio
async def test_policy_search_emits_document_count(monkeypatch):
    calls = _record(monkeypatch, "distribution")

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


def _fake_run(events):
    async def stream_events():
        for event in events:
            yield event

    return SimpleNamespace(stream_events=stream_events, to_input_list=lambda: [])


async def _drain(session, message="hi"):
    return [frame async for frame in chat_stream.stream_turn(session, message)]


@pytest.mark.asyncio
async def test_turn_emits_tool_call_count(monkeypatch):
    calls = _record(monkeypatch, "distribution")
    events = [
        RunItemStreamEvent(
            name="tool_called",
            item=SimpleNamespace(raw_item={"name": "ask_checkout_agent", "call_id": c}),
        )
        for c in ("c1", "c2")
    ]
    monkeypatch.setattr(
        chat_stream.Runner, "run_streamed", lambda *a, **k: _fake_run(events)
    )

    await _drain(ChatSession("m2"))

    assert calls == [("agent.turn.tool_calls", 2, {"attributes": {"agent": "manager"}})]


@pytest.mark.asyncio
async def test_turn_without_tools_emits_zero(monkeypatch):
    calls = _record(monkeypatch, "distribution")
    monkeypatch.setattr(
        chat_stream.Runner, "run_streamed", lambda *a, **k: _fake_run([])
    )

    await _drain(ChatSession("m3"))

    assert [(n, v) for n, v, _ in calls] == [("agent.turn.tool_calls", 0)]
