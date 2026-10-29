"""search_policies returns the pages that answer the question, as plain text.

It used to ignore the query and return the whole help-centre export as raw HTML
(~160KB, ~47k input tokens on the next LLM call). These tests keep it to the
matching pages, markup-free, and keep the history guard for oversized results.
"""

import json

import pytest
from test_tool_errors import _run_in_tool_span

from app.session import OMITTED_TOOL_RESULT, ChatSession, trim_tool_outputs
from app.tools.shop import search_policies
from app.tools.shop.policies import MAX_PAGES
from app.tools.shop.policy_export import PAGE_COUNT, RETURNS_PAGE_TITLE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query", ["return policy", "What is your return policy?", "shipping to Canada"]
)
async def test_only_matching_pages_are_returned_as_plain_text(query):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    assert PAGE_COUNT == 50
    assert 0 < len(payload["pages"]) <= MAX_PAGES
    for page in payload["pages"]:
        assert set(page) == {"title", "text"}
        assert "<" not in page["text"] and "&" not in page["text"]
    assert len(json.dumps(payload)) < 4_000


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["return policy", "What is your return policy?"])
async def test_return_question_finds_the_returns_page(query):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p2")
    )

    first = payload["pages"][0]
    assert first["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in first["text"]
    assert "5–7 business days" in first["text"]


@pytest.mark.asyncio
async def test_shipping_question_ranks_shipping_pages_first():
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "shipping to Canada"}, ChatSession("p3")
    )

    titles = [page["title"] for page in payload["pages"]]
    assert titles[:2] == ["Shipping times and carriers", "International shipping"]


@pytest.mark.asyncio
async def test_unmatched_question_returns_no_pages_and_no_card():
    session = ChatSession("p4")
    payload, span = await _run_in_tool_span(
        search_policies, {"query": "zzyzx"}, session
    )

    assert payload["pages"] == []
    assert span["data"]["policy.pages"] == 0
    assert session.drain_widgets() == []


@pytest.mark.asyncio
async def test_span_reports_the_returned_size():
    payload, span = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("p5")
    )

    assert span["data"]["policy.pages"] == len(payload["pages"])
    assert span["data"]["policy.bytes"] == pytest.approx(
        len(json.dumps(payload)), rel=0.01
    )
    assert span.get("status") != "internal_error"


@pytest.mark.asyncio
async def test_card_carries_the_answer_not_the_export():
    session = ChatSession("p6")
    await _run_in_tool_span(search_policies, {"query": "return policy"}, session)

    (widget,) = session.drain_widgets()
    assert widget["type"] == "policy"
    assert widget["data"]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in widget["data"]["excerpt"]
    assert "<" not in widget["data"]["excerpt"]
    assert len(json.dumps(widget)) < 1024
    assert session.last_tool == "search_policies"


@pytest.mark.asyncio
async def test_card_follows_the_question():
    session = ChatSession("p7")
    await _run_in_tool_span(search_policies, {"query": "shipping to Canada"}, session)

    (widget,) = session.drain_widgets()
    assert widget["data"]["title"] != RETURNS_PAGE_TITLE


def test_oversized_latest_result_is_still_collapsed():
    blob = json.dumps({"pages": ["x" * 20_000]})
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_checkout_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": blob},
    ]

    assert trim_tool_outputs(history)[1]["output"] == OMITTED_TOOL_RESULT.format(
        tool="ask_checkout_agent"
    )


def test_ordinary_latest_result_is_still_kept():
    products = json.dumps({"products": [{"id": 1, "title": "Plant Mood"}] * 10})
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_products_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": products},
    ]

    assert trim_tool_outputs(history)[1]["output"] == products
