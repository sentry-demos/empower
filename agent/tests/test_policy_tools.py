"""search_policies answers a policy question with the matching pages only.

The tool used to ignore the query and return the whole help-centre export as raw
HTML (~160KB, ~47k input tokens on the next LLM call). These tests assert the
corrected behaviour: only relevant pages, as plain text, in a normal turn's worth
of tokens, with the answer still in them.
"""

import json

import pytest
from test_tool_errors import _run_in_tool_span

from app.session import ChatSession, trim_tool_outputs
from app.tools.shop import search_policies
from app.tools.shop.policies import MAX_PAGES
from app.tools.shop.policy_export import PAGE_COUNT, RETURNS_PAGE_TITLE


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["return policy", "What is your return policy?"])
async def test_returns_question_gets_the_returns_page(query):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    assert payload["pages"][0]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in payload["pages"][0]["text"]


@pytest.mark.asyncio
async def test_other_questions_get_their_own_pages():
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "shipping to Canada"}, ChatSession("p1b")
    )

    titles = [page["title"] for page in payload["pages"]]
    assert "International shipping" in titles
    assert len(titles) <= MAX_PAGES


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["return policy", "shipping to Canada", ""])
async def test_only_a_few_pages_come_back_as_plain_text(query):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p2")
    )

    assert len(payload["pages"]) <= MAX_PAGES < PAGE_COUNT
    for page in payload["pages"]:
        assert set(page) == {"title", "text"}
        assert "<" not in page["text"]


@pytest.mark.asyncio
async def test_payload_is_small_and_reported_on_the_span():
    payload, span = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("p3")
    )

    size = len(json.dumps(payload))
    # A normal turn is ~1k tokens; the raw export was ~160KB.
    assert size < 4_000
    assert span["data"]["policy.pages"] == len(payload["pages"])
    assert span["data"]["policy.bytes"] == pytest.approx(size, rel=0.01)
    assert span.get("status") != "internal_error"


@pytest.mark.asyncio
async def test_unmatched_question_lists_topics_instead_of_dumping_pages():
    session = ChatSession("p4")
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "quantum chromodynamics"}, session
    )

    assert payload["pages"] == []
    assert RETURNS_PAGE_TITLE in payload["available_topics"]
    assert len(json.dumps(payload)) < 4_000
    assert session.drain_widgets() == []


@pytest.mark.asyncio
async def test_card_carries_the_answer_not_the_export():
    session = ChatSession("p5")
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
    session = ChatSession("p6")
    await _run_in_tool_span(search_policies, {"query": "gift cards"}, session)

    (widget,) = session.drain_widgets()
    assert widget["data"]["title"] == "Gift cards"


@pytest.mark.asyncio
async def test_latest_result_is_kept_for_the_next_turn():
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("p7")
    )
    output = json.dumps(payload)
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_checkout_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": output},
    ]

    assert trim_tool_outputs(history)[1]["output"] == output


def test_ordinary_latest_result_is_still_kept():
    products = json.dumps({"products": [{"id": 1, "title": "Plant Mood"}] * 10})
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_products_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": products},
    ]

    assert trim_tool_outputs(history)[1]["output"] == products
