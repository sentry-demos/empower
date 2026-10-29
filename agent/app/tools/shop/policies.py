"""Store policy lookup, backed by a mock help-centre export.

search_policies finds the pages of the export that answer the customer's
question and returns their text, without the export's markup. checkout_agent
stops on its first tool, so whatever this returns becomes the delegation's
result verbatim and lands in the orchestrator's next gen_ai.chat call: it has
to be just the answer, not the help centre.
"""

import html
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

# Most pages handed to the model for one question.
MAX_PAGES = 3

# A title match counts for more than the same word somewhere in the body.
TITLE_WEIGHT = 3

_TAGS = re.compile(r"<[^>]+>")
_WORDS = re.compile(r"[a-z0-9]+")
_SUFFIXES = ("ing", "es", "ed", "s")

# Words that say nothing about which page is wanted. "policy" is here because
# "return policy" must find "Returns & refunds", not every page called a policy.
_FILLER = {
    "a", "an", "and", "are", "about", "can", "do", "does", "for", "how", "i",
    "in", "is", "it", "me", "my", "of", "on", "or", "the", "to", "what",
    "when", "where", "with", "you", "your",
}  # fmt: skip
_GENERIC = {"policy", "policies"}


def _stem(word: str) -> str:
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _terms(query: str) -> list[str]:
    words = [w for w in _WORDS.findall(query.lower()) if w not in _FILLER]
    specific = [w for w in words if w not in _GENERIC]
    return [_stem(w) for w in specific or words]


def _body_text(page_html: str) -> str:
    """A page's body copy as plain text, without the export's page chrome."""
    body = page_html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split('<div class="page-metadata">', 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    return " ".join(html.unescape(_TAGS.sub("", body)).split())


def _excerpt(text: str) -> str:
    return text[:EXCERPT_CHARS]


def _find_pages(query: str) -> list[dict[str, Any]]:
    """The best-matching pages, most relevant first, as title and plain text."""
    terms = _terms(query)
    scored = []
    for page in policy_export.pages():
        text = _body_text(page["html"])
        title_words = _WORDS.findall(page["title"].lower())
        body_words = _WORDS.findall(text.lower())
        score = sum(
            TITLE_WEIGHT * any(w.startswith(t) for w in title_words)
            + any(w.startswith(t) for w in body_words)
            for t in terms
        )
        if score:
            scored.append((score, {"title": page["title"], "text": text}))
    scored.sort(key=lambda match: -match[0])  # stable: ties keep export order
    return [page for _, page in scored[:MAX_PAGES]]


@function_tool  # type: ignore[misc]
async def search_policies(context: RunContextWrapper[ChatSession], query: str) -> str:
    """Search the help centre for store policies.

    Args:
        query: What the customer wants to know, e.g. "return policy".

    Returns:
        JSON with the help centre pages that best match, as plain text.
    """
    session = context.context
    logging.debug(f"search_policies query={query!r}")

    pages = _find_pages(query)
    payload = json.dumps({"query": query, "pages": pages})

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    if pages:
        session.record_widget(
            "search_policies",
            "policy",
            {"title": pages[0]["title"], "excerpt": _excerpt(pages[0]["text"])},
        )
    return payload
