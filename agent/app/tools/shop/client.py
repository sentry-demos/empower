"""Shared httpx client for talking to the Flask backend from inside a tool.

httpx is pinned explicitly in requirements.txt (rather than coming along
transitively with openai) so sentry-sdk's httpx integration is active and each
call produces an http.client span under the gen_ai.execute_tool span.
"""

import os
from typing import Any

import httpx

from ...utils import request_headers

# Headers worth re-sending downstream. main.py's middleware reads these off the
# browser request; forwarding them keeps flask's spans tagged the same way the
# agent's are.
_FORWARDED_HEADERS = ("se", "customerType", "email", "cexp")

# Flask /products is slow by design, and the 'extremely slow' profile is slower
# still, so allow well past a default 5s timeout.
REQUEST_TIMEOUT_SECONDS = 60.0


def flask_url() -> str:
    """Base URL of the Flask backend.

    Read at call time, not import time, so a missing FLASK_URL doesn't take the
    whole app down with it — /buy-plants doesn't need this.

    When flask runs locally, FLASK_URL is http://localhost:$FLASK_LOCAL_PORT,
    which from inside this container means the container itself. Rewrite it to
    reach the host (docker-compose.yml maps host.docker.internal for this).
    Doing it here rather than in run_local.sh is deliberate: `deploy` drops any
    variable whose value still contains __GCP_SECRET__ from the environment it
    hands to run_local.sh, and FLASK_URL is one of them when pointing at a
    deployed host. Deployed URLs contain no 'localhost', so this is a no-op
    on Cloud Run.
    """
    url = os.environ.get("FLASK_URL")
    if not url:
        raise RuntimeError(
            "FLASK_URL is not set; the shopping tools need the Flask backend."
        )

    if os.path.exists("/.dockerenv"):
        for local_host in ("localhost", "127.0.0.1"):
            url = url.replace(f"//{local_host}:", "//host.docker.internal:")

    return url.rstrip("/")


def outbound_headers() -> dict[str, str]:
    """Demo/routing headers to attach to a downstream Flask call."""
    incoming = request_headers.get()
    return {
        name: incoming[name]
        for name in _FORWARDED_HEADERS
        if incoming.get(name) not in (None, "", "undefined")
    }


async def get(path: str, params: dict[str, Any] | None = None) -> Any:
    """GET a Flask endpoint, returning the decoded JSON body."""
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{flask_url()}{path}", params=params, headers=outbound_headers()
        )
        response.raise_for_status()
        return response.json()
