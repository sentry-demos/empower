"""search_policies must return only the pages that answer the query, as text.

It used to ignore the query and return the whole help-centre export as raw HTML
(~160KB, ~47k input tokens on the next LLM call).
"""

import json

import pytest
from test_tool_errors import _run_in_tool_span

from app.session import OMITTED_TOOL_RESULT, ChatSession, trim_tool_outputs
from app.tools.shop import search_policies
from app.tools.shop.policies import MAX_RESULTS
from app.tools.shop.policy_export import RETURNS_PAGE_TITLE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query", ["return policy", "What is your return policy?", "shipping to Canada"]
)
async def test_payload_is_small_plain_text(query):
    payload, span = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    size = len(json.dumps(payload))
    assert 0 < len(payload["pages"]) <= MAX_RESULTS
    assert size < 5_000
    assert all("<" not in page["text"] for page in payload["pages"])
    assert span["data"]["policy.pages"] == len(payload["pages"])
    assert span["data"]["policy.bytes"] == pytest.approx(size, rel=0.01)
    assert span.get("status") != "internal_error"


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["return policy", "What is your return policy?"])
async def test_return_question_gets_the_returns_page_first(query):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p2")
    )

    assert payload["pages"][0]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in payload["pages"][0]["text"]


@pytest.mark.asyncio
async def test_unrelated_query_returns_no_pages_and_no_card():
    session = ChatSession("p3")
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "xyzzy"}, session
    )

    assert payload["pages"] == []
    assert session.drain_widgets() == []


@pytest.mark.asyncio
async def test_card_carries_the_answer():
    session = ChatSession("p4")
    await _run_in_tool_span(search_policies, {"query": "return policy"}, session)

    (widget,) = session.drain_widgets()
    assert widget["type"] == "policy"
    assert widget["data"]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in widget["data"]["excerpt"]
    assert "<" not in widget["data"]["excerpt"]
    assert len(json.dumps(widget)) < 1024
    assert session.last_tool == "search_policies"


def test_ordinary_latest_result_is_still_kept():
    products = json.dumps({"products": [{"id": 1, "title": "Plant Mood"}] * 10})
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_products_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": products},
    ]

    assert trim_tool_outputs(history)[1]["output"] == products


def test_omitted_marker_still_exported():
    assert "{tool}" in OMITTED_TOOL_RESULT
