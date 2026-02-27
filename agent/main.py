"""Main FastAPI application for the AI Agent."""

import os
import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.openai_agents import OpenAIAgentsIntegration

from app.api.routes import router
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


# Create FastAPI app
app = FastAPI(
    title="Empower Plant Shopping Agent",
    description="AI shopping assistant for plant care gadgets and accessories",
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

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["agent"])


@app.get("/")  # type: ignore[misc]
async def root() -> dict[str, str]:
    """Root endpoint with basic information."""
    return {
        "message": "Welcome to Empower Plant Shopping Agent",
        "docs": "/docs",
        "health": "/api/v1/health",
        "chat": "/api/v1/chat",
        "version": "2.0.0",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
