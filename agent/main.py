"""Main FastAPI application for the AI Agent."""

import os
import sentry_sdk
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.openai_agents import OpenAIAgentsIntegration
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.api.routes import router
from config import settings


def propagate_context_to_spans(event, hint):
    """Copy request-context tags onto every span's attributes.

    The sentry_event_context middleware sets `se`/`customerType`/`cexp` as
    event-level tags (and `email` as the user), which only land on the root
    http.server span. The auto-instrumented gen_ai.* child spans don't inherit
    them, so we mirror the values onto each span's `data` here.
    """
    tags = event.get("tags") or {}
    attrs = {
        key: tags[key]
        for key in ("se", "customerType", "cexp")
        if tags.get(key) is not None
    }
    email = (event.get("user") or {}).get("email")
    if email is not None:
        attrs["user.email"] = email

    if not attrs:
        return event

    for span in event.get("spans", []):
        span.setdefault("data", {}).update(attrs)

    trace = (event.get("contexts") or {}).get("trace")
    if trace is not None:
        trace.setdefault("data", {}).update(attrs)

    return event


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
    before_send_transaction=propagate_context_to_spans,
)


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
