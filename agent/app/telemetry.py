"""Sentry wiring: which project each part of the agent reports to.

The service spans three projects:

    main agent run  -> AGENT_DSN           (the conversation itself)
    product lookups -> AGENT_PLANT_DSN     (catalogue / search)
    checkout        -> AGENT_SHOPPING_DSN  (cart, coupon, order)

A Sentry transaction belongs to exactly one project, and every span inside a
single Runner.run() is a child of the same transaction — so a tool cannot simply
be tagged into a different project. Each routed tool instead opens its OWN
transaction on its own client and rejoins the parent trace by trace id, the same
way tracing already works across services. The result is one trace in Sentry's
trace view whose spans are split across projects, with the parent's
gen_ai.execute_tool span sitting directly above the routed transaction.
"""

import os
from contextlib import contextmanager
from typing import Any, Iterator

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.openai_agents import OpenAIAgentsIntegration


def propagate_context_to_spans(event: Any, hint: Any) -> Any:
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


def sentry_options(dsn: str) -> dict[str, Any]:
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


# Built once on first use rather than at import, so a missing DSN degrades to
# "report to the main project" instead of breaking startup.
_clients: dict[str, sentry_sdk.Client | None] = {}


def _client(env_var: str) -> sentry_sdk.Client | None:
    if env_var not in _clients:
        dsn = os.environ.get(env_var) or ""
        _clients[env_var] = sentry_sdk.Client(**sentry_options(dsn)) if dsn else None
    return _clients[env_var]


def plant_client() -> sentry_sdk.Client | None:
    """Project for product/catalogue work."""
    return _client("AGENT_PLANT_DSN")


def shopping_client() -> sentry_sdk.Client | None:
    """Project for cart and checkout work."""
    return _client("AGENT_SHOPPING_DSN")


@contextmanager
def routed_transaction(
    client: sentry_sdk.Client | None, op: str, name: str
) -> Iterator[None]:
    """Run the block as its own transaction on `client`, inside the current trace.

    Falls through to the caller's own transaction when `client` is None, so an
    unset DSN just means those spans stay in the main project.
    """
    if client is None:
        yield
        return

    # Captured before switching scopes, so the new transaction inherits this
    # trace and shows up as a child of the parent's execute_tool span.
    headers = dict(sentry_sdk.get_current_scope().iter_trace_propagation_headers())

    with sentry_sdk.isolation_scope() as scope:
        scope.set_client(client)
        transaction = sentry_sdk.continue_trace(headers, op=op, name=name)
        with sentry_sdk.start_transaction(transaction):
            yield


@contextmanager
def tool_span(client: sentry_sdk.Client | None, tool_name: str) -> Iterator[None]:
    """routed_transaction with the naming the gen_ai tool spans use."""
    with routed_transaction(client, "gen_ai.execute_tool", f"execute_tool {tool_name}"):
        yield
