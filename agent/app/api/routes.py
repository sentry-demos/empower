"""Simple API routes for the plant care agent."""


from fastapi import APIRouter, HTTPException

from ..agents.manager_agent import process_user_request
from .models import ChatResponse, HealthResponse, PlantPurchaseRequest

# Initialize router
router = APIRouter()


@router.get("/health", response_model=HealthResponse)  # type: ignore[misc]
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", agent_name="", version="1.0.0")


@router.post("/buy-plants", response_model=ChatResponse)  # type: ignore[misc]
async def buy_plants(request: PlantPurchaseRequest) -> ChatResponse:
    """Trigger the plant purchase workflow.

    Args:
        request: Request containing light and maintenance preferences

    Returns:
        Confirmation of plant purchase

    Raises:
        HTTPException: If processing fails
    """
    try:
        response = await process_user_request(
            light=request.light, maintenance=request.maintenance
        )

        return ChatResponse(response=response, agent_name="manager_agent")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process plant purchase: {str(e)}"
        )
