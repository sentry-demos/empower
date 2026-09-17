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

import logging
import os
from contextlib import contextmanager
from typing import Any, Iterator

import sentry_sdk
from sentry_sdk.consts import OP, SPANSTATUS
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.openai_agents import OpenAIAgentsIntegration
from sentry_sdk.traces import SpanStatus, StreamedSpan


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


def mark_tool_error(error_type: str, message: str) -> None:
    """Mark the enclosing gen_ai.execute_tool span as failed.

    The agents integration only fails that span when the tool raises: it looks
    for the SDK's "An error occurred while running the tool" string in the
    result. The shopping tools deliberately don't raise — the expired coupon
    (410) and the inventory failure (500) are the demo, and the customer is
    meant to read the backend's own wording — so the failure arrives as an
    ordinary JSON result and the span would otherwise finish green.

    Setting the status here is what puts those calls in Sentry's Tool Errors
    widget. `error.type` is the attribute that view reads; the message rides
    along as span data for whoever opens the span.

    https://docs.sentry.io/platforms/python/agent-tracing/manual-instrumentation/
    """
    span = sentry_sdk.get_current_span()
    if span is None:
        logging.debug(f"no span open to mark as a tool error: {message}")
        return

    # Both span implementations, the way the SDK's own integration handles them:
    # the streaming one (_experiments trace_lifecycle="stream", off here) keeps
    # its op in an attribute and takes a plain ok/error status.
    #
    # The check itself is that we are where we think we are: this is called from
    # inside the tool body, where the integration's execute_tool span is the
    # innermost open span (the httpx child has already finished). If that ever
    # stops being true, say so rather than failing some unrelated span.
    if isinstance(span, StreamedSpan):
        op = span.get_attributes().get("sentry.op")
        if op != OP.GEN_AI_EXECUTE_TOOL:
            logging.debug(f"not marking {op!r} as a tool error: {message}")
            return

        span.status = SpanStatus.ERROR
        span.set_attribute("error.type", error_type)
        span.set_attribute("error.message", message)
    else:
        if span.op != OP.GEN_AI_EXECUTE_TOOL:
            logging.debug(f"not marking {span.op!r} as a tool error: {message}")
            return

        span.set_status(SPANSTATUS.INTERNAL_ERROR)
        span.set_data("error.type", error_type)
        span.set_data("error.message", message)


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
def agent_transaction(
    client: sentry_sdk.Client | None, agent_name: str
) -> Iterator[None]:
    """Run a sub-agent as its own transaction in that agent's project.

    Deliberately not op=gen_ai.invoke_agent named "invoke_agent <agent>": that is
    what sentry_sdk's agents integration emits inside this block, and reusing the
    name made things appear twice in the AI Agent timeline. This transaction is
    the routed container that span sits in, so it is named as its own unit.
    """
    with routed_transaction(client, "function", f"agent {agent_name}"):
        yield
