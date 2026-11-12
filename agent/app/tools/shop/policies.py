"""Store policy lookup, backed by a mock help-centre export.

search_policies finds the pages that match the customer's question and returns
only those, as plain text. checkout_agent stops on its first tool, so this
result becomes the delegation's result verbatim and lands in the orchestrator's
next gen_ai.chat call; it must stay small. (It used to return every page of the
export as raw HTML, ~160KB or ~47k input tokens.) policy.pages and policy.bytes
on the tool span record the size.
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


MAX_RESULTS = 3
_WORDS = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "is", "it",
    "my", "of", "on", "or", "the", "to", "what", "your", "you", "we", "about",
}  # fmt: skip


def _body_text(html: str) -> str:
    """A page's body copy, without the export's markup or page chrome."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1]
    # The body ends at the wiki-content div's close. Nested macro divs are
    # flattened by stripping tags, so cut at the page-metadata block instead.
    body = body.split('<div class="page-metadata">', 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _stem(word: str) -> str:
    return word[:-1] if len(word) > 3 and word.endswith("s") else word


def _terms(text: str) -> set[str]:
    return {_stem(w) for w in _WORDS.findall(text.lower()) if w not in _STOPWORDS}


def _search(query: str) -> list[dict]:
    """The pages that best match the query, best first, as plain text."""
    wanted = _terms(query)
    scored = []
    for page in policy_export.pages():
        text = _body_text(page["html"])
        title_hits = len(wanted & _terms(page["title"]))
        body_hits = len(wanted & _terms(text))
        score = 3 * title_hits + body_hits
        if score:
            scored.append((score, page, text))
    scored.sort(key=lambda item: -item[0])
    return [
        {"id": page["id"], "title": page["title"], "text": text}
        for _, page, text in scored[:MAX_RESULTS]
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
