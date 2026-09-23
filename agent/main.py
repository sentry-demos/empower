"""Main FastAPI application for the AI Agent."""

import os
import sentry_sdk
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.api.routes import router
from app.telemetry import sentry_options
from app.utils import request_headers
from config import settings

# The conversation itself — this endpoint's transactions and the agent's
# gen_ai.* spans. Product and checkout tools open their own transactions on
# their own projects; see app/telemetry.py.
sentry_sdk.init(**sentry_options(os.environ["AGENT_DSN"]))


# Create FastAPI app
app = FastAPI(
    title="Simple Plant Care API",
    description="Simple AI plant care assistant - just provide a plant name!",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Extract context information
@app.middleware("http")
async def sentry_event_context(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
    se = request.headers.get("se")
    customer_type = request.headers.get("customerType")
    email = request.headers.get("email")
    cexp = request.headers.get("cexp")

    if se not in (None, "undefined"):
        sentry_sdk.set_tag("se", se)

    if customer_type not in (None, "undefined"):
        sentry_sdk.set_tag("customerType", customer_type)

    if email not in (None, "undefined"):
        sentry_sdk.set_user({"email": email})

    if cexp not in (None, "undefined"):
        sentry_sdk.set_tag("cexp", cexp)

    # The tags above only reach the agent's own transaction. Stash the raw
    # values so tools making outbound Flask calls can forward them, keeping the
    # downstream flask spans tagged the same way.
    request_headers.set(
        {
            "se": se or "",
            "customerType": customer_type or "",
            "email": email or "",
            "cexp": cexp or "",
        }
    )

    return await call_next(request)


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["agent"])


@app.get("/")  # type: ignore[misc]
async def root() -> dict[str, str]:
    """Root endpoint with basic information."""
    return {
        "message": "Welcome to the Simple Plant Care API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "agent_info": "/api/v1/agent/info",
        "plant_care": "/api/v1/plant-care",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
