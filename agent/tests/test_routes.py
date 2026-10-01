"""The plant-lookup failure triggers, on the real /chat route.

`agent_advice_error` / `agent_info_error` are set on the page URL; ChatWidget.jsx
maps them onto ?validate_plant_advice / ?validate_plant_info on the agent
request. /buy-plants read them from the start. /chat did not, which quietly
killed both demo error paths for the conversational flow — including in
_tda/desktop_web/test_ai_agent.py, which still appends those page params and
still drives the chat widget.

These go through the router rather than calling set_plant_failure_flags()
directly, so removing the call from the endpoint fails them. `stream_turn` is
stubbed out: the flags are read inside a tool, deep inside a real LLM turn, so
the stub reports them from the same place a tool would — while the response body
is being streamed, after the handler has returned.
"""

from typing import AsyncIterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import routes
from app.utils import validate_plant_advice, validate_plant_info


@pytest.fixture
def client(monkeypatch):
    """A client for the real router, with the LLM turn stubbed out."""

    async def fake_stream_turn(session, message: str) -> AsyncIterator[str]:
        yield f"{validate_plant_advice.get()},{validate_plant_info.get()}"

    monkeypatch.setattr(routes, "stream_turn", fake_stream_turn)
    monkeypatch.setattr(routes, "get_session", lambda conversation_id: None)

    app = FastAPI()
    app.include_router(routes.router, prefix="/api/v1")
    return TestClient(app)


def post_turn(client, query: str = ""):
    return client.post(
        f"/api/v1/chat{query}",
        json={"message": "show me plants"},
        headers={"x-conversation-id": "conv-test"},
    )


@pytest.mark.parametrize(
    "query, expected",
    [
        ("", "False,False"),
        ("?validate_plant_advice=true", "True,False"),
        ("?validate_plant_info=true", "False,True"),
        ("?validate_plant_advice=true&validate_plant_info=true", "True,True"),
        # Anything that isn't "true" is no failure. TRUE is, since the widget
        # passes the page param's value through verbatim.
        ("?validate_plant_advice=TRUE", "True,False"),
        ("?validate_plant_advice=false", "False,False"),
        ("?validate_plant_advice=1", "False,False"),
    ],
)
def test_a_turn_is_armed_from_the_query_string(client, query, expected):
    response = post_turn(client, query)
    assert response.status_code == 200
    assert response.text == expected


def test_flags_do_not_leak_into_the_next_turn(client):
    assert post_turn(client, "?validate_plant_info=true").text == "False,True"
    assert post_turn(client).text == "False,False"


def test_a_turn_still_needs_a_conversation_id(client):
    response = client.post("/api/v1/chat", json={"message": "hi"})
    assert response.status_code == 400
