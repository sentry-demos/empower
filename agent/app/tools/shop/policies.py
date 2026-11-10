"""Store policy lookup, backed by a mock help-centre export.

search_policies returns only the few pages that match the customer's query, as
plain text with the export's markup stripped. checkout_agent stops on its first
tool, so this result becomes the delegation's result verbatim and lands in the
orchestrator's next gen_ai.chat call; returning the whole raw export (~160KB)
once cost tens of thousands of input tokens for one policy question.
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

_STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is",
    "it", "me", "my", "of", "on", "or", "the", "to", "what", "your", "you",
}  # fmt: skip


def _body_text(html: str) -> str:
    """A page's body copy (below the title), without markup or page chrome."""
    body = html.split('class="wiki-content"', 1)[-1]
    # Keep everything to the end of the main-content div, nested divs included.
    body = body.split("</h1>", 1)[-1].split('<div class="page-metadata">', 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    return _body_text(html)[:EXCERPT_CHARS]


def _terms(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w.rstrip("s") or w for w in words if w not in _STOPWORDS]


def _matching_pages(query: str) -> list[dict]:
    """The best MAX_PAGES pages for the query, as plain text. Title hits count more."""
    terms = _terms(query)
    scored = []
    for page in policy_export.pages():
        text = _body_text(page["html"])
        title_words = _terms(page["title"])
        body_words = set(_terms(text))
        score = sum(
            3 * any(w.startswith(t) for w in title_words) + (t in body_words)
            for t in terms
        )
        if score:
            scored.append((score, {"id": page["id"], "title": page["title"], "text": text}))
    scored.sort(key=lambda item: -item[0])
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

    pages = _matching_pages(query)
    payload = json.dumps({"query": query, "pages": pages})

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    answer = next(
        page
        for page in policy_export.pages()
        if page["title"] == policy_export.RETURNS_PAGE_TITLE
    )
    session.record_widget(
        "search_policies",
        "policy",
        {"title": answer["title"], "excerpt": _excerpt(answer["html"])},
    )
    return payload
