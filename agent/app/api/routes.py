"""Simple API routes for the plant care agent."""


import sentry_sdk.ai
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from ..agents.manager_agent import process_user_request
from ..session import get_session
from ..utils import validate_plant_advice, validate_plant_info
from .chat_stream import stream_turn
from .models import (
    ChatResponse,
    ChatTurnRequest,
    HealthResponse,
    PlantPurchaseRequest,
)

# Initialize router
router = APIRouter()


def set_plant_failure_flags(raw_request: Request) -> None:
    """Arm the plant-lookup failures from the request's query params.

    ?validate_plant_advice=true makes the plant advice lookup fail;
    ?validate_plant_info=true makes the plant basic info lookup fail.
    Unset/anything else is false (no failure).

    Both endpoints need this: ChatWidget.jsx maps the operator-facing
    `agent_advice_error` / `agent_info_error` page params onto these for /chat
    the same way it used to for /buy-plants, and test_ai_agent.py drives those
    two error paths through the chat widget.

    Called from the endpoint rather than from inside stream_turn: the handler
    and the StreamingResponse body it returns run in the same task, so a
    contextvar set here is visible while the turn streams.
    """
    validate_plant_advice.set(
        raw_request.query_params.get("validate_plant_advice", "").lower() == "true"
    )
    validate_plant_info.set(
        raw_request.query_params.get("validate_plant_info", "").lower() == "true"
    )


@router.get("/health", response_model=HealthResponse)  # type: ignore[misc]
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", agent_name="", version="1.0.0")


@router.post("/chat")  # type: ignore[misc]
async def chat(request: ChatTurnRequest, raw_request: Request) -> StreamingResponse:
    """Run one conversational shopping turn, streamed back as SSE.

    Separate from /buy-plants, which keeps serving the original scripted flow.

    Args:
        request: The customer's message
        raw_request: Raw FastAPI request for reading headers

    Returns:
        A text/event-stream of status / token / widget / pills / done events

    Raises:
        HTTPException: If the conversation id is missing
    """
    conversation_id = raw_request.headers.get("x-conversation-id")
    if not conversation_id:
        raise HTTPException(status_code=400, detail="x-conversation-id is required")

    sentry_sdk.ai.set_conversation_id(conversation_id)
    set_plant_failure_flags(raw_request)
    session = get_session(conversation_id)

    return StreamingResponse(
        stream_turn(session, request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            # Tell any nginx in front of Cloud Run not to buffer the stream,
            # which would defeat the point of streaming it.
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/buy-plants", response_model=ChatResponse)  # type: ignore[misc]
async def buy_plants(
    request: PlantPurchaseRequest, raw_request: Request
) -> ChatResponse:
    """Trigger the plant purchase workflow.

    Args:
        request: Request containing light and maintenance preferences
        raw_request: Raw FastAPI request for reading headers

    Returns:
        Confirmation of plant purchase

    Raises:
        HTTPException: If processing fails
    """
    conversation_id = raw_request.headers.get("x-conversation-id")
    if conversation_id:
        sentry_sdk.ai.set_conversation_id(conversation_id)

    set_plant_failure_flags(raw_request)

    try:
        response = await process_user_request(
            light=request.light, maintenance=request.maintenance
        )

        return ChatResponse(response=response, agent_name="manager_agent")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process plant purchase: {str(e)}"
        )
