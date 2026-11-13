"""Store policy lookup, backed by a mock help-centre export.

search_policies returns only the few pages that match the customer's query, as
plain text. checkout_agent stops on its first tool, so this result becomes the
delegation's result verbatim and lands in the orchestrator's next gen_ai.chat
call; returning the whole raw HTML export (~160KB) used to cost ~47k input
tokens per policy question.
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
    "a", "an", "the", "is", "are", "what", "your", "you", "do", "does", "how",
    "to", "for", "of", "and", "or", "i", "my", "can", "me", "about", "on", "in",
}  # fmt: skip
_WORDS = re.compile(r"[a-z0-9]+")


def _body_text(html: str) -> str:
    """A page's body copy, without the export's markup or page chrome."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split('<div class="page-metadata"', 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    return _body_text(html)[:EXCERPT_CHARS]


def _terms(text: str) -> set[str]:
    # Crude plural folding so "return" finds "Returns & refunds".
    return {
        w[:-1] if len(w) > 3 and w.endswith("s") else w
        for w in _WORDS.findall(text.lower())
        if w not in _STOPWORDS
    }


def _search(query: str) -> list[dict]:
    """The pages that best match the query: title hits weigh more than body hits."""
    wanted = _terms(query)
    scored = []
    for page in policy_export.pages():
        title = _terms(page["title"])
        body = _terms(_body_text(page["html"]))
        score = 3 * len(wanted & title) + len(wanted & body)
        if score:
            scored.append((score, page))
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

    matches = _search(query)
    pages = [{"title": p["title"], "text": _body_text(p["html"])} for p in matches]
    payload = json.dumps({"query": query, "pages": pages})

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    if matches:
        session.record_widget(
            "search_policies",
            "policy",
            {"title": matches[0]["title"], "excerpt": _excerpt(matches[0]["html"])},
        )
    return payload
