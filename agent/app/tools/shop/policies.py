"""Store policy lookup, backed by a mock help-centre export.

search_policies finds the pages that answer the customer's question and returns
only those, as plain text. checkout_agent stops on its first tool, so this
output becomes the delegation's result verbatim and lands in the orchestrator's
next gen_ai.chat call; it must stay small. Returning the whole export as raw
HTML (~160KB, ~47k tokens) used to spike that call's input tokens.
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


# How many pages are handed to the model for one question.
MAX_PAGES = 3

_WORDS = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is",
    "it", "my", "of", "on", "or", "the", "to", "what", "your", "you", "about",
}  # fmt: skip


def _body_text(html: str) -> str:
    """A page's body copy, without the export's chrome or markup."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split("</div>", 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _stems(text: str) -> set[str]:
    """Lower-cased words, cut to 5 letters so "returns" matches "return"."""
    return {w[:5] for w in _WORDS.findall(text.lower()) if w not in _STOPWORDS}


def _score(query_stems: set[str], title: str, text: str) -> int:
    """Title matches count triple; body matches count once."""
    return 3 * len(query_stems & _stems(title)) + len(query_stems & _stems(text))


def _search(query: str) -> list[dict[str, str]]:
    """The best-matching pages as {title, text}, best first, at most MAX_PAGES."""
    query_stems = _stems(query)
    scored = []
    for page in policy_export.pages():
        text = _body_text(page["html"])
        score = _score(query_stems, page["title"], text)
        if score:
            scored.append((score, {"title": page["title"], "text": text}))
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

    # Only the pages that match the question, as plain text.
    pages = _search(query)
    payload = json.dumps({"query": query, "pages": pages})

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    if pages:
        answer = pages[0]
        session.record_widget(
            "search_policies",
            "policy",
            {"title": answer["title"], "excerpt": answer["text"][:EXCERPT_CHARS]},
        )
    return payload
