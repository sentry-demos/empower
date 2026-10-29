"""Store policy lookup, backed by a mock help-centre export.

search_policies finds the help-centre pages that match the customer's question
and returns only those, as plain text. checkout_agent stops on its first tool, so
this result is what the orchestrator reads on its next gen_ai.chat call: it has
to be the answer, not the export (the raw export is ~160KB of HTML, ~47k tokens).
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

# Pages handed to the model. Enough for a question that touches a few topics,
# few enough that the result stays a normal turn's size.
MAX_PAGES = 3

# Every page here is a policy page, so these words say nothing about which one.
_STOPWORDS = frozenset(
    "a an and are can do does for how i in is it me my of on or the to what"
    " when where which with you your policy policies".split()
)
_TITLE_WEIGHT = 3

_TAGS = re.compile(r"<[^>]+>")
_WORDS = re.compile(r"[a-z0-9]+")


def _body_text(html: str) -> str:
    """A page's body copy without markup, chrome or the page title."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split("</div>", 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    return _body_text(html)[:EXCERPT_CHARS]


def _stems(text: str) -> set[str]:
    """Lower-cased words minus stopwords, with a plural "s" dropped."""
    return {
        word[:-1] if len(word) > 3 and word.endswith("s") else word
        for word in _WORDS.findall(text.lower().replace("&", " "))
        if word not in _STOPWORDS
    }


def _search(query: str) -> list[dict[str, Any]]:
    """The best MAX_PAGES pages for the query, most relevant first."""
    terms = _stems(query)
    scored = []
    for page in policy_export.pages():
        text = _body_text(page["html"])
        score = len(terms & _stems(page["title"])) * _TITLE_WEIGHT + len(
            terms & _stems(text)
        )
        if score:
            scored.append((score, page, text))
    # sorted is stable, so equally relevant pages keep their help-centre order.
    scored.sort(key=lambda match: -match[0])
    return [
        {"id": page["id"], "title": page["title"], "text": text, "html": page["html"]}
        for _, page, text in scored[:MAX_PAGES]
    ]


@function_tool  # type: ignore[misc]
async def search_policies(context: RunContextWrapper[ChatSession], query: str) -> str:
    """Search the help centre for store policies.

    Args:
        query: What the customer wants to know, e.g. "return policy".

    Returns:
        JSON with the best matching help centre pages as plain text, or the list
        of help centre topics if nothing matched.
    """
    session = context.context
    logging.debug(f"search_policies query={query!r}")

    matches = _search(query)
    result: dict[str, Any] = {
        "query": query,
        "pages": [
            {"title": match["title"], "text": match["text"]} for match in matches
        ],
    }
    if not matches:
        result["available_topics"] = [page["title"] for page in policy_export.pages()]
    payload = json.dumps(result)

    set_tool_attribute("policy.pages", len(matches))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(matches)} pages, {len(payload)} bytes")

    if matches:
        session.record_widget(
            "search_policies",
            "policy",
            {"title": matches[0]["title"], "excerpt": _excerpt(matches[0]["html"])},
        )
    return payload
