"""search_policies emits the number of documents it sends to the model."""

import json

import pytest
import sentry_sdk
from test_tool_errors import _run_in_tool_span

from app.session import ChatSession
from app.tools.shop import search_policies


@pytest.mark.asyncio
async def test_policy_documents_metric_is_emitted(monkeypatch):
    calls = []
    monkeypatch.setattr(
        sentry_sdk.metrics,
        "distribution",
        lambda name, value, **kwargs: calls.append((name, value, kwargs)),
    )

    payload, _ = await _run_in_tool_span(
        search_policies, {"query": "return policy"}, ChatSession("m1")
    )

    assert len(calls) == 1
    name, value, kwargs = calls[0]
    assert name == "agent.policy.documents"
    assert value == len(payload["pages"])
    assert kwargs["attributes"] == {"tool": "search_policies"}
