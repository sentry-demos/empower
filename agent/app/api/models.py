"""Pydantic models for API requests and responses."""


from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="Agent's response")
    agent_name: str = Field(..., description="Name of the responding agent")

    class Config:
        schema_extra = {
            "example": {
                "response": "Yellow leaves on a pothos can indicate overwatering...",
                "agent_name": "EmpowerPlantAgent",
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
