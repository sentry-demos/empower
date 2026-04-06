"""Pydantic models for API requests and responses."""


from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for conversational chat endpoint."""

    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User's message")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "I'm looking for a gift for a plant lover",
            }
        }


class ResponseItem(BaseModel):
    """Individual response item with type and content."""

    type: Literal["message", "product_card", "checkout_result"] = Field(
        ..., description="Type of response item"
    )
    content: dict[str, Any] = Field(..., description="Content payload for this item")

    class Config:
        schema_extra = {
            "examples": [
                {"type": "message", "content": {"text": "What's your budget?"}},
                {"type": "product_card", "content": {"id": 1, "name": "Plant Mood", "price": 155}},
                {"type": "checkout_result", "content": {"success": False, "error": "Out of stock"}},
            ]
        }


class ChatResponse(BaseModel):
    """Response model for conversational chat endpoint."""

    session_id: str = Field(..., description="Session identifier")
    items: list[ResponseItem] = Field(..., description="List of response items")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "items": [
                    {"type": "message", "content": {"text": "Based on your answers, I recommend:"}},
                    {"type": "product_card", "content": {"id": 3, "name": "Plant Mood", "price": 155}},
                ],
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service status")
    agent_name: str = Field(..., description="Agent name")
    version: str = Field(..., description="API version")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "agent_name": "shopping_agent",
                "version": "1.0.0",
            }
        }
