"""Store policy lookup, backed by a mock help-centre export.

search_policies finds the pages that answer the customer's question and returns
only those, as plain text. checkout_agent stops on its first tool, so this
output becomes the delegation's result verbatim and lands in the orchestrator's
next gen_ai.chat call; it must stay small. (It used to return every page of the
export as raw HTML, ~160KB / ~47k tokens.)
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


# Pages returned to the model per question; the best match is first.
MAX_PAGES = 3

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is",
    "it", "me", "my", "of", "on", "or", "the", "to", "what", "when", "your", "you",
}  # fmt: skip


def _body_text(html: str) -> str:
    """A page's body copy (the wiki content, not the export chrome) as plain text."""
    body = html.split('class="wiki-content"', 1)[-1]
    # Keep the whole content div: a page may hold nested divs (info macros).
    body = body.split("</h1>", 1)[-1].split('<div class="page-metadata"', 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _stem(word: str) -> str:
    return word[:-1] if len(word) > 3 and word.endswith("s") else word


def _terms(text: str) -> set[str]:
    return {_stem(w) for w in _WORD.findall(text.lower()) if w not in _STOPWORDS}


def _search(query: str) -> list[dict[str, str]]:
    """The best-matching pages for the query as {title, text}, best first."""
    wanted = _terms(query)
    scored = []
    for page in policy_export.pages():
        text = _body_text(page["html"])
        title_terms, body_terms = _terms(page["title"]), _terms(text)
        score = 3 * len(wanted & title_terms) + len(wanted & body_terms)
        if score:
            scored.append((score, {"title": page["title"], "text": text}))
    scored.sort(key=lambda item: -item[0])  # stable: export order breaks ties
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
