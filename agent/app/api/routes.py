"""Simple API routes for the plant care agent."""


import sentry_sdk.ai
from fastapi import APIRouter, HTTPException, Request

from ..agents.manager_agent import process_user_request
from ..utils import agent_crash_mode
from .models import ChatResponse, HealthResponse, PlantPurchaseRequest

# Initialize router
router = APIRouter()


@router.get("/health", response_model=HealthResponse)  # type: ignore[misc]
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", agent_name="", version="1.0.0")


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

    # ?agent_crash=true forces the plant advice error every time; =false
    # suppresses all injected errors; absent falls back to random probabilities.
    agent_crash = raw_request.query_params.get("agent_crash")
    agent_crash_mode.set(
        None if agent_crash is None else agent_crash.lower() == "true"
    )

    try:
        response = await process_user_request(
            light=request.light, maintenance=request.maintenance
        )

        return ChatResponse(response=response, agent_name="manager_agent")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process plant purchase: {str(e)}"
        )
