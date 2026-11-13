"""search_policies must return only the pages relevant to the question.

Returning the whole help-centre export as raw HTML cost ~48k input tokens per
policy question, so these tests pin down that the payload is small, is plain
text, and still contains the answer.
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
    "query", ["return policy", "What is your return policy?", "shipping to Canada"]
)
async def test_only_matching_pages_are_returned_as_text(query):
    payload, span = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    assert 0 < len(payload["pages"]) <= MAX_PAGES
    assert len(json.dumps(payload)) < 5_000
    for page in payload["pages"]:
        assert "<" not in page["text"]
        assert "html" not in page
    assert span["data"]["policy.pages"] == len(payload["pages"])


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["return policy", "What is your return policy?"])
async def test_return_question_gets_the_returns_page(query):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p2")
    )

    assert payload["pages"][0]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in payload["pages"][0]["text"]


@pytest.mark.asyncio
async def test_unrelated_query_returns_no_pages():
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "xyzzy"}, ChatSession("p3")
    )

    assert payload["pages"] == []


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


def test_large_latest_result_is_still_collapsed_in_history():
    session = ChatSession("p5")
    session.remember(
        [
            {"role": "user", "content": "What is your return policy?"},
            {"type": "function_call", "call_id": "c1", "name": "ask_checkout_agent"},
            {
                "type": "function_call_output",
                "call_id": "c1",
                "output": json.dumps({"blob": "x" * 150_000}),
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
