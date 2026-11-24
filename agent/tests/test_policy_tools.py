"""search_policies returns only the pages that answer the question, as text.

Regression tests for the context snowball: the tool used to return the whole
help-centre export as raw HTML (~160KB, ~47k input tokens on the next LLM
call). Also covered: the chat card stays small, and the next turn's history
doesn't carry the tool result at all.
"""

import json

import pytest
from test_tool_errors import _run_in_tool_span

from app.session import OMITTED_TOOL_RESULT, ChatSession, trim_tool_outputs
from app.tools.shop import search_policies
from app.tools.shop.policies import MAX_PAGES
from app.tools.shop.policy_export import PAGE_COUNT, RETURNS_PAGE_TITLE


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["return policy", "shipping to Canada", ""])
async def test_only_matching_pages_are_returned_as_text(query):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    assert len(payload["pages"]) <= MAX_PAGES < PAGE_COUNT
    for page in payload["pages"]:
        assert set(page) == {"title", "text"}
        assert "<" not in page["text"]


@pytest.mark.asyncio
async def test_returns_question_gets_its_answer_in_a_small_payload():
    payload, span = await _run_in_tool_span(
        search_policies, {"query": "What is your return policy?"}, ChatSession("p2")
    )

    size = len(json.dumps(payload))
    assert size < 5_000
    assert payload["pages"][0]["title"] == RETURNS_PAGE_TITLE
    assert "30 days" in payload["pages"][0]["text"]
    assert span["data"]["policy.pages"] == len(payload["pages"])
    assert span["data"]["policy.bytes"] == pytest.approx(size, rel=0.01)
    assert span.get("status") != "internal_error"


@pytest.mark.asyncio
async def test_other_questions_get_other_pages():
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "shipping to Canada"}, ChatSession("p2b")
    )

    titles = [page["title"] for page in payload["pages"]]
    assert titles[:2] == ["Shipping times and carriers", "International shipping"]


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
async def test_policy_result_is_small_enough_to_keep_in_history():
    """The result is no longer oversized, so history keeps it as it is."""
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

    assert session.history[2]["output"] == json.dumps(blob)
    assert OMITTED_TOOL_RESULT.format(tool="ask_checkout_agent") not in json.dumps(
        session.history
    )
    assert len(json.dumps(session.history)) < 5_000


def test_ordinary_latest_result_is_still_kept():
    products = json.dumps({"products": [{"id": 1, "title": "Plant Mood"}] * 10})
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_products_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": products},
    ]

    assert trim_tool_outputs(history)[1]["output"] == products
