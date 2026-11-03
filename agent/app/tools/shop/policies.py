"""Store policy lookup, backed by a mock help-centre export.

search_policies finds the pages that answer the customer's question and returns
only those, as plain text. checkout_agent stops on its first tool, so this
result becomes the delegation's result verbatim and lands in the orchestrator's
next gen_ai.chat call; it must stay small. (It used to return every page of the
export as raw HTML, ~160KB / ~47k tokens.)
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


MAX_RESULTS = 3
# Words that say "this is a policy question" without saying which policy.
_STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "you", "your", "to", "for",
    "of", "on", "in", "and", "or", "what", "how", "can", "i", "my", "we",
    "policy", "policies", "about", "tell", "me",
}  # fmt: skip


def _terms(text: str) -> set[str]:
    """Lower-cased, singularised search words, minus stopwords."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words} - _STOPWORDS


def _page_text(html: str) -> str:
    """A page's body copy without the export's navigation, styles and scripts."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split('<div class="page-metadata">', 1)[0]
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _search(query: str) -> list[dict[str, Any]]:
    """The pages that best match the query, as plain text, best first."""
    wanted = _terms(query)
    scored = []
    for page in policy_export.pages():
        text = _page_text(page["html"])
        score = 3 * len(wanted & _terms(page["title"])) + len(wanted & _terms(text))
        if score:
            scored.append((score, {"title": page["title"], "text": text}))
    scored.sort(key=lambda item: -item[0])
    return [page for _, page in scored[:MAX_RESULTS]]


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

    pages = _search(query)
    payload = json.dumps({"query": query, "pages": pages})

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    if pages:
        session.record_widget(
            "search_policies",
            "policy",
            {"title": pages[0]["title"], "excerpt": pages[0]["text"][:EXCERPT_CHARS]},
        )
    return payload
