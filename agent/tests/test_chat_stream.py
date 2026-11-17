"""Agent attribution on the chat stream.

The chat shows which agent produced each card and each reply. That mapping is a
plain dict, so the way it breaks is by omission: someone adds a shopping tool,
wires up its card, and the card renders with no badge — or worse, with the
orchestrator's, crediting the wrong agent. These tests fail at that point
instead.
"""

from types import SimpleNamespace

import pytest
import sentry_sdk
from agents.stream_events import RunItemStreamEvent

from app.api import chat_stream
from app.session import ChatSession
from app.api.chat_stream import (
    AGENTS,
    DEFAULT_AGENT,
    DELEGATION_CLAIMS,
    SPEAKER_AGENTS,
    STATUS_LABELS,
    TOOL_AGENTS,
    WIDGET_TYPES,
    agent_ref,
)


def test_every_announced_tool_names_an_agent():
    """A tool that puts up a ticker has to say whose ticker it is."""
    missing = set(STATUS_LABELS) - set(TOOL_AGENTS)
    assert not missing, f"no TOOL_AGENTS entry for {missing}"


def test_every_card_producing_tool_names_an_agent():
    """Same for the tools that record cards — this is the badge on the card."""
    missing = set(WIDGET_TYPES) - set(TOOL_AGENTS)
    assert not missing, f"no TOOL_AGENTS entry for {missing}"


def test_mappings_only_reference_known_agents():
    unknown = {
        agent_id
        for agent_id in (*TOOL_AGENTS.values(), *SPEAKER_AGENTS.values())
        if agent_id not in AGENTS
    }
    assert not unknown, f"not in AGENTS: {unknown}"


def test_delegation_claims_cover_the_orchestrators_specialists():
    """The keys ask_*_agent passes to claim_delegation, which is how the stream
    tells "the specialist ran" from "the specialist was refused"."""
    assert DELEGATION_CLAIMS == {
        "ask_products_agent": "products_agent",
        "ask_checkout_agent": "checkout_agent",
    }


def test_agent_ref_falls_back_rather_than_raising():
    """An unmapped tool should cost a badge, not the turn."""
    assert agent_ref("plant") == {"id": "plant", "name": AGENTS["plant"]}
    assert agent_ref(None)["id"] == DEFAULT_AGENT
    assert agent_ref("no_such_agent")["id"] == DEFAULT_AGENT


@pytest.mark.asyncio
async def test_turn_emits_tool_call_count(monkeypatch):
    def item(name, call_id):
        return SimpleNamespace(raw_item={"name": name, "call_id": call_id})

    class FakeResult:
        async def stream_events(self):
            yield RunItemStreamEvent(
                name="tool_called", item=item("ask_checkout_agent", "c1")
            )
            yield RunItemStreamEvent(
                name="tool_called", item=item("ask_products_agent", "c2")
            )

        def to_input_list(self):
            return []

    monkeypatch.setattr(
        chat_stream.Runner, "run_streamed", lambda *a, **k: FakeResult()
    )
    calls = []
    monkeypatch.setattr(
        sentry_sdk.metrics,
        "distribution",
        lambda name, value, **kw: calls.append((name, value, kw)),
    )

    async for _ in chat_stream.stream_turn(ChatSession("t1"), "hi"):
        pass

    assert calls == [
        (
            "agent.turn.tool_calls",
            2,
            {"attributes": {"agent": chat_stream.SHOPPING_AGENT_NAME}},
        )
    ]
