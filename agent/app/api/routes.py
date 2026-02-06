"""API routes for the Empower Plant shopping agent."""


import sentry_sdk.ai
from fastapi import APIRouter, HTTPException, Request

from ..agents.manager_agent import process_chat_message, process_user_request
from .models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    LegacyChatResponse,
    PlantPurchaseRequest,
)

# Initialize router
router = APIRouter()


@router.get("/health", response_model=HealthResponse)  # type: ignore[misc]
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", agent_name="shopping_agent", version="2.0.0")


@router.post("/chat", response_model=ChatResponse)  # type: ignore[misc]
async def chat(request: ChatRequest) -> ChatResponse:
    """Conversational chat endpoint with session support.
    
    This endpoint maintains conversation history using SQLiteSession.
    Each session_id represents a unique conversation thread.
    
    Args:
        request: Chat request with session_id and message
        
    Returns:
        Structured response with message items, product cards, or checkout results
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        items = await process_chat_message(
            session_id=request.session_id,
            message=request.message
        )
        
        return ChatResponse(
            session_id=request.session_id,
            items=items
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.post("/buy-plants", response_model=LegacyChatResponse)  # type: ignore[misc]
async def buy_plants(request: PlantPurchaseRequest) -> LegacyChatResponse:
    """Legacy endpoint for plant purchase workflow.
    
    Kept for backward compatibility. For new integrations, use /chat endpoint.

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

    try:
        response = await process_user_request(
            light=request.light, maintenance=request.maintenance
        )

        return LegacyChatResponse(response=response, agent_name="shopping_agent")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process plant purchase: {str(e)}"
        )
