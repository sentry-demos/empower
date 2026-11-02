"""search_policies must return only the pages that answer the question, as text.

Returning the whole help-centre export as raw HTML cost tens of thousands of
input tokens per policy question. These tests also cover the chat card and the
next turn's history.
"""

import json

import pytest
from test_tool_errors import _run_in_tool_span

from app.session import ChatSession, trim_tool_outputs
from app.tools.shop import search_policies
from app.tools.shop.policy_export import PAGE_COUNT, RETURNS_PAGE_TITLE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query", ["return policy", "What is your return policy?", "shipping to Canada"]
)
async def test_only_matching_pages_are_returned_as_text(query):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    assert PAGE_COUNT == 50
    assert 0 < len(payload["pages"]) <= 3
    # Extracted text, not raw export HTML.
    assert all("<" not in page["text"] for page in payload["pages"])
    assert all("html" not in page for page in payload["pages"])


@pytest.mark.asyncio
async def test_return_question_gets_its_answer_in_a_small_payload():
    payload, span = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("p2")
    )

    size = len(json.dumps(payload))
    assert size < 5_000
    assert payload["pages"][0]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in payload["pages"][0]["text"]
    assert span["data"]["policy.pages"] == len(payload["pages"])
    assert span["data"]["policy.bytes"] == pytest.approx(size, rel=0.01)
    assert span.get("status") != "internal_error"


@pytest.mark.asyncio
async def test_unmatched_query_returns_no_pages():
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "xyzzy"}, ChatSession("p6")
    )

    assert payload["pages"] == []


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
async def test_policy_answer_keeps_history_small():
    """The policy result no longer bloats the next turn's history."""
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

    # The policy answer is small now, so it is kept as ordinary history.
    assert session.history[2]["output"] == json.dumps(blob)
    assert len(json.dumps(session.history)) < 3_000


def test_ordinary_latest_result_is_still_kept():
    products = json.dumps({"products": [{"id": 1, "title": "Plant Mood"}] * 10})
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_products_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": products},
    ]

    assert trim_tool_outputs(history)[1]["output"] == products
