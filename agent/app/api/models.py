"""Pydantic models for API requests and responses."""


from typing import Any, Literal

from pydantic import BaseModel, Field


# Legacy response model (kept for backward compatibility)
class LegacyChatResponse(BaseModel):
    """Legacy response model for buy-plants endpoint."""

    response: str = Field(..., description="Agent's response")
    agent_name: str = Field(..., description="Name of the responding agent")

    class Config:
        schema_extra = {
            "example": {
                "response": "Yellow leaves on a pothos can indicate overwatering...",
                "agent_name": "EmpowerPlantAgent",
            }
        }


# New chat models
class ChatRequest(BaseModel):
    """Request model for conversational chat endpoint."""

    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User's message")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "I'm looking for a low-maintenance plant",
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
                {"type": "message", "content": {"text": "What kind of light does your space get?"}},
                {"type": "product_card", "content": {"id": 1, "name": "Monstera", "price": 29.99}},
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
                    {"type": "product_card", "content": {"id": 1, "name": "Monstera", "price": 29.99}},
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
                "agent_name": "EmpowerPlantAgent",
                "version": "1.0.0",
            }
        }


class PlantPurchaseRequest(BaseModel):
    """Request model for plant purchase endpoint."""

    light: str = Field(..., description="Light conditions for the plants", min_length=1)
    maintenance: str = Field(
        ..., description="Maintenance level for the plants", min_length=1
    )

    class Config:
        schema_extra = {"example": {"light": "full sun", "maintenance": "low"}}
