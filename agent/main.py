"""Main FastAPI application for the AI Agent.

The application includes an integrated API tester that runs as a background task
during the FastAPI lifespan. The tester periodically calls various API endpoints
to simulate realistic usage patterns.

Configuration:
- API_TESTER_ENABLED: Enable/disable the API tester (default: true)
- API_TESTER_BASE_INTERVAL_MS: Base interval between calls in milliseconds
  (default: 120000)
- API_TESTER_JITTER_PERCENT: Percentage of jitter to add to intervals
  (default: 30)
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import os
import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.openai_agents import OpenAIAgentsIntegration

from app.api.routes import router
from app.jobs import api_tester
from config import settings

sentry_sdk.init(
    dsn=os.environ["AGENT_DSN"],
    environment=os.environ["AGENT_SENTRY_ENVIRONMENT"],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations=[
        FastApiIntegration(),
        OpenAIAgentsIntegration(),
    ],
    disabled_integrations=[OpenAIIntegration()],
    send_default_pii=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    print("🚀 Starting Simple Plant Care API...")

    # Start the API tester background task
    try:
        await api_tester.start()
    except Exception as e:
        print(f"⚠️  API tester failed to start: {e}")

    yield

    # Stop the API tester background task
    try:
        await api_tester.stop()
    except Exception as e:
        print(f"⚠️  API tester failed to stop gracefully: {e}")

    print("🛑 Shutting down Simple Plant Care API...")


# Create FastAPI app
app = FastAPI(
    title="Simple Plant Care API",
    description="Simple AI plant care assistant - just provide a plant name!",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
