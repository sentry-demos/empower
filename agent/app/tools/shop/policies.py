"""Store policy lookup, backed by a mock help-centre export.

search_policies returns only the few pages that match the query, as plain text.
checkout_agent stops on its first tool, so this result becomes the delegation's
result verbatim and lands in the orchestrator's next gen_ai.chat call; returning
the whole raw export (~160KB) once cost ~48k input tokens per policy question.
"""

import json
import logging
import re
from typing import Any

from agents import RunContextWrapper, function_tool

from ...session import ChatSession
from ...telemetry import set_tool_attribute
from . import policy_export

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# How much of the answering page the chat card shows. The card is all that goes
# to the browser: the full payload would otherwise travel over SSE as well, and
# from there into Session Replay.
EXCERPT_CHARS = 200

_TAGS = re.compile(r"<[^>]+>")

# At most this many pages go back to the model.
MAX_PAGES = 3
_STOPWORDS = {"the", "and", "what", "your", "you", "are", "for", "how", "can", "does",
              "our", "with", "about", "from", "this", "that", "have", "any"}


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split("</div>", 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())[:EXCERPT_CHARS]


def _text(html: str) -> str:
    """A page's title and body copy as plain text, without the export's chrome."""
    title = html.split("<h1>", 1)[-1].split("</h1>", 1)[0]
    body = html.split('class="wiki-content"', 1)[-1].split("</h1>", 1)[-1]
    body = body.split('<div class="page-metadata"', 1)[0].replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return f"{title}: {' '.join(text.split())}"


def _terms(text: str) -> set[str]:
    """Lower-cased words, crudely singularised, minus filler words."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w.rstrip("s") for w in words if len(w) > 2 and w not in _STOPWORDS}


def _match(query: str, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The MAX_PAGES pages that best match the query; none if nothing overlaps."""
    wanted = _terms(query)
    scored = []
    for page in pages:
        title_hits = len(wanted & _terms(page["title"]))
        body_hits = len(wanted & _terms(_text(page["html"])))
        score = 3 * title_hits + body_hits
        if score:
            scored.append((score, page))
    scored.sort(key=lambda s: -s[0])  # stable: ties keep export order
    return [page for _, page in scored[:MAX_PAGES]]


@function_tool  # type: ignore[misc]
async def search_policies(context: RunContextWrapper[ChatSession], query: str) -> str:
    """Search the help centre for store policies.

    Args:
        query: What the customer wants to know, e.g. "return policy".

    Returns:
        JSON with the matching help centre pages.
    """
    session = context.context
    logging.debug(f"search_policies query={query!r}")

    pages = _match(query, policy_export.pages())
    payload = json.dumps(
        {
            "query": query,
            "pages": [{"title": p["title"], "text": _text(p["html"])} for p in pages],
        }
    )

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    if pages:
        session.record_widget(
            "search_policies",
            "policy",
            {"title": pages[0]["title"], "excerpt": _excerpt(pages[0]["html"])},
        )
    else:
        session.last_tool = "search_policies"
    return payload
