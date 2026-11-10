"""Store policy lookup, backed by a mock help-centre export.

search_policies finds the pages that answer the customer's question and returns
only those, as plain text. It used to ignore the query and return every page of
the export as raw HTML (~160KB); checkout_agent stops on its first tool, so that
blob became the delegation's result and landed in the orchestrator's next
gen_ai.chat call as ~48k input tokens.
"""

import json
import logging
import re

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


MAX_PAGES = 3

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "is", "it",
    "my", "of", "on", "or", "the", "to", "what", "your", "you", "me", "about",
}  # fmt: skip


def _body_text(html: str) -> str:
    """A page's body copy, without the export's markup."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    # Drop the trailing page chrome (metadata, footer, scripts) after the content div.
    body = re.split(r'<div class="page-metadata"', body, 1)[0]
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    return _body_text(html)[:EXCERPT_CHARS]


def _terms(text: str) -> set[str]:
    # Crude plural stripping so "returns" matches "return".
    return {
        w[:-1] if len(w) > 3 and w.endswith("s") else w
        for w in _WORD.findall(text.lower())
        if w not in _STOPWORDS
    }


def _best_pages(query: str, pages: list[dict]) -> list[dict]:
    """The pages that best match the query, as plain text, best first."""
    wanted = _terms(query)
    scored = []
    for page in pages:
        text = _body_text(page["html"])
        score = 3 * len(wanted & _terms(page["title"])) + len(wanted & _terms(text))
        if score:
            scored.append((score, page, text))
    scored.sort(key=lambda s: -s[0])  # stable: ties keep export order
    return [
        {"id": page["id"], "title": page["title"], "text": text}
        for _, page, text in scored[:MAX_PAGES]
    ]


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

    matches = _best_pages(query, policy_export.pages())
    payload = json.dumps({"query": query, "pages": matches})

    set_tool_attribute("policy.pages", len(matches))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(matches)} pages, {len(payload)} bytes")

    if matches:
        session.record_widget(
            "search_policies",
            "policy",
            {
                "title": matches[0]["title"],
                "excerpt": matches[0]["text"][:EXCERPT_CHARS],
            },
        )
    return payload
