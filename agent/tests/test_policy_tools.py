"""search_policies returns only the pages that answer the question.

It once ignored the query and returned the whole help-centre export as raw
HTML (~160KB, ~47k input tokens on the next chat turn). These tests pin the
small, relevant, markup-free payload.
"""

import json

import pytest
from test_tool_errors import _run_in_tool_span

from app.session import OMITTED_TOOL_RESULT, ChatSession, trim_tool_outputs
from app.tools.shop import search_policies
from app.tools.shop.policies import MAX_PAGES
from app.tools.shop.policy_export import RETURNS_PAGE_TITLE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query", ["return policy", "What is your return policy?", "shipping to Canada", ""]
)
async def test_payload_is_small_plain_text(query):
    payload, span = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    assert len(payload["pages"]) <= MAX_PAGES
    assert len(json.dumps(payload)) < 5_000
    assert "<" not in json.dumps(payload["pages"])
    assert span["data"]["policy.pages"] == len(payload["pages"])
    assert span.get("status") != "internal_error"


@pytest.mark.asyncio
async def test_return_question_gets_the_returns_page_first():
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("p2")
    )

    assert payload["pages"][0]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in payload["pages"][0]["text"]


@pytest.mark.asyncio
async def test_shipping_question_gets_shipping_pages():
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "shipping to Canada"}, ChatSession("p2b")
    )

    titles = [p["title"] for p in payload["pages"]]
    assert titles[:2] == ["Shipping times and carriers", "International shipping"]


@pytest.mark.asyncio
async def test_card_carries_the_answer():
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
async def test_no_match_returns_no_pages_and_no_card():
    session = ChatSession("p3b")
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "zzzxqv"}, session
    )

    assert payload["pages"] == []
    assert session.drain_widgets() == []


@pytest.mark.asyncio
async def test_oversized_result_is_still_collapsed_in_history():
    """Defence in depth: a big tool result is dropped from the next turn's history."""
    blob = {"pages": [{"title": "x", "text": "y" * 200_000}]}
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
