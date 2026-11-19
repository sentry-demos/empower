"""search_policies must return only the pages relevant to the question, as text.

It once returned the whole help-centre export as raw HTML (~160KB, ~47k input
tokens on the next chat turn), whatever the query. These tests assert the
correct behaviour: a few matching pages, no markup, answer included.
"""

import json

import pytest
from test_tool_errors import _run_in_tool_span

from app.session import ChatSession, trim_tool_outputs
from app.tools.shop import search_policies
from app.tools.shop.policies import MAX_PAGES
from app.tools.shop.policy_export import RETURNS_PAGE_TITLE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query", ["return policy", "What is your return policy?", "shipping to Canada", ""]
)
async def test_only_matching_pages_are_returned(query):
    payload, span = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    assert len(payload["pages"]) <= MAX_PAGES
    assert len(json.dumps(payload)) < 8_000
    assert span["data"]["policy.pages"] == len(payload["pages"])
    # Extracted text, not raw export HTML.
    for page in payload["pages"]:
        assert "<" not in page["text"]
        assert "html" not in page


@pytest.mark.asyncio
async def test_return_question_gets_the_returns_page_first():
    payload, span = await _run_in_tool_span(
        search_policies, {"query": "What is your return policy?"}, ChatSession("p2")
    )

    assert payload["pages"][0]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in payload["pages"][0]["text"]
    assert span.get("status") != "internal_error"


@pytest.mark.asyncio
async def test_unrelated_question_does_not_return_the_returns_page():
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "shipping to Canada"}, ChatSession("p3")
    )

    titles = [page["title"] for page in payload["pages"]]
    assert "International shipping" in titles
    assert titles[0] != RETURNS_PAGE_TITLE


@pytest.mark.asyncio
async def test_card_carries_the_answer_not_the_export():
    session = ChatSession("p4")
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
    session = ChatSession("p5")
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "zzzqqq"}, session
    )

    assert payload["pages"] == []
    assert session.drain_widgets() == []


def test_ordinary_latest_result_is_still_kept():
    products = json.dumps({"products": [{"id": 1, "title": "Plant Mood"}] * 10})
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_products_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": products},
    ]

    assert trim_tool_outputs(history)[1]["output"] == products
