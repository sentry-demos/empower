"""search_policies, the context snowball.

The tool ignores the query and returns the whole help-centre export as raw
HTML. That is the demo — one policy question costing tens of thousands of input
tokens — so these tests pin the oversized payload down on purpose, along with
the two things that keep it contained: the chat card stays small, and the next
turn's history doesn't carry the blob at all.
"""

import json

import pytest
from test_tool_errors import _run_in_tool_span

from app.session import OMITTED_TOOL_RESULT, ChatSession, trim_tool_outputs
from app.tools.shop import search_policies
from app.tools.shop.policy_export import PAGE_COUNT, RETURNS_PAGE_TITLE


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["return policy", "shipping to Canada", ""])
async def test_every_page_is_returned_whatever_the_query(query):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    assert PAGE_COUNT == 50
    assert len(payload["pages"]) == PAGE_COUNT
    # Raw export HTML, chrome and all — not extracted text.
    assert all(page["html"].startswith("<!DOCTYPE html>") for page in payload["pages"])


@pytest.mark.asyncio
async def test_payload_is_big_enough_to_spike_input_tokens():
    payload, span = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("p2")
    )

    size = len(json.dumps(payload))
    # ~3KB a page. Roughly 40k tokens against a 1-2k baseline turn.
    assert 120_000 < size < 200_000
    assert span["data"]["policy.pages"] == PAGE_COUNT
    assert span["data"]["policy.bytes"] == pytest.approx(size, rel=0.01)
    # Nothing failed; that is the point.
    assert span.get("status") != "internal_error"


@pytest.mark.asyncio
async def test_card_carries_the_answer_not_the_export():
    session = ChatSession("p3")
    await _run_in_tool_span(search_policies, {"query": "return policy"}, session)

    (widget,) = session.drain_widgets()
    assert widget["type"] == "policy"
    assert widget["data"]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in widget["data"]["excerpt"]
    assert "<" not in widget["data"]["excerpt"]
    assert len(json.dumps(widget)) < 1024
    assert session.last_tool == "search_policies"


@pytest.mark.asyncio
async def test_spike_is_one_turn_wide():
    """The blob is collapsed before the next turn, though it is the latest."""
    blob, _ = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("p4")
    )
    session = ChatSession("p5")
    session.remember(
        [
            {"role": "user", "content": "What is your return policy?"},
            {"type": "function_call", "call_id": "c1", "name": "ask_checkout_agent"},
            {
                "type": "function_call_output",
                "call_id": "c1",
                "output": json.dumps(blob),
            },
            {"role": "assistant", "content": "Returns are accepted within 30 days."},
        ]
    )

    assert session.history[2]["output"] == OMITTED_TOOL_RESULT.format(
        tool="ask_checkout_agent"
    )
    assert len(json.dumps(session.history)) < 2_000


def test_ordinary_latest_result_is_still_kept():
    products = json.dumps({"products": [{"id": 1, "title": "Plant Mood"}] * 10})
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_products_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": products},
    ]

    assert trim_tool_outputs(history)[1]["output"] == products
