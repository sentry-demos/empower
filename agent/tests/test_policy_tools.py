"""search_policies: returns only the matching pages, as plain text.

Regression tests for the context snowball, where the tool ignored the query and
returned the whole help-centre export as raw HTML (~160KB, ~48k input tokens).
Also covers the two things that keep a big result contained: the chat card
stays small, and the next turn's history doesn't carry a large tool blob.
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
    "query,title",
    [
        ("return policy", RETURNS_PAGE_TITLE),
        ("What is your return policy?", RETURNS_PAGE_TITLE),
        ("shipping to Canada", "International shipping"),
    ],
)
async def test_only_matching_pages_are_returned_as_text(query, title):
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": query}, ChatSession("p1")
    )

    assert 0 < len(payload["pages"]) <= MAX_PAGES
    assert title in [page["title"] for page in payload["pages"]]
    assert all("<" not in page["text"] for page in payload["pages"])


@pytest.mark.asyncio
async def test_return_answer_survives_and_payload_is_small():
    payload, span = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("p2")
    )

    size = len(json.dumps(payload))
    assert "30 days" in json.dumps(payload)
    assert size < 8_000  # was ~160KB
    assert span["data"]["policy.pages"] == len(payload["pages"])
    assert span["data"]["policy.bytes"] == pytest.approx(size, rel=0.01)
    assert span.get("status") != "internal_error"


@pytest.mark.asyncio
async def test_unmatched_query_returns_no_pages_and_no_card():
    session = ChatSession("p2b")
    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "xyzzy"}, session
    )

    assert payload["pages"] == []
    assert session.drain_widgets() == []


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
    """The latest result is now small, so history keeps it and stays small."""
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
    assert len(json.dumps(session.history)) < 4_000


def test_ordinary_latest_result_is_still_kept():
    products = json.dumps({"products": [{"id": 1, "title": "Plant Mood"}] * 10})
    history = [
        {"type": "function_call", "call_id": "c1", "name": "ask_products_agent"},
        {"type": "function_call_output", "call_id": "c1", "output": products},
    ]

    assert trim_tool_outputs(history)[1]["output"] == products
