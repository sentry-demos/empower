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
from app.utils import request_headers
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


def _sentry_options(dsn: str) -> dict:
    """Client options shared by every Sentry project this service reports to."""
    return dict(
        dsn=dsn,
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


# Default client: the conversational shopping flow, and anything not routed below.
sentry_sdk.init(**_sentry_options(os.environ["AGENT_DSN"]))

# The original /buy-plants flow reports to its own project. A transaction belongs
# to exactly one project, and handoff spans are children of the same transaction,
# so routing is necessarily per-endpoint rather than per-agent: manager_agent's
# handoff to plant_expert_agent stays inside the /buy-plants transaction. Doing it
# this way leaves manager_agent and plant_expert_agent themselves untouched.
_manager_dsn = os.environ.get("AGENT_MANAGER_DSN") or ""
manager_client = sentry_sdk.Client(**_sentry_options(_manager_dsn)) if _manager_dsn else None


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


# Endpoints whose transactions belong to a Sentry project other than the default.
_CLIENT_BY_PATH: dict[str, sentry_sdk.Client] = (
    {"/api/v1/buy-plants": manager_client} if manager_client else {}
)


async def asgi(scope: dict, receive: object, send: object) -> None:
    """Pick the Sentry project for this request, then hand off to FastAPI.

    This has to sit outside the FastAPI app: the Starlette integration patches
    Starlette.__call__ itself, so SentryAsgiMiddleware is the outermost layer
    inside `app` and the transaction already exists by the time any middleware
    or route code of ours runs. Binding the client on an isolation scope out
    here means the transaction is created on the right client — Sentry's own
    isolation scope forks from this one and inherits it.
    """
    client = _CLIENT_BY_PATH.get(scope.get("path", "")) if scope.get("type") == "http" else None
    if client is None:
        await app(scope, receive, send)  # type: ignore[arg-type]
        return

    with sentry_sdk.isolation_scope() as isolation_scope:
        isolation_scope.set_client(client)
        await app(scope, receive, send)  # type: ignore[arg-type]


if __name__ == "__main__":
    uvicorn.run(
        "main:asgi",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
