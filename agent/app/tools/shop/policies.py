"""Store policy lookup, backed by a mock help-centre export.

search_policies returns the few pages that match the customer's query, as plain
text. checkout_agent stops on its first tool, so this result becomes the
delegation's result verbatim and lands in the orchestrator's next gen_ai.chat
call; it has to stay small. (It once returned all ~50 export pages as raw HTML,
~160KB / ~47k input tokens.) policy.pages and policy.bytes on the tool span
record what was returned.
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

# Pages returned to the model per question.
MAX_PAGES = 3

_STOPWORDS = {"the", "what", "your", "you", "are", "and", "for", "how", "can",
              "does", "do", "is", "to", "of", "a", "our", "with", "about", "policy"}


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split("</div>", 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())[:EXCERPT_CHARS]


def _page_text(html: str) -> str:
    """A page's body copy without the export's chrome or markup."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split('<div class="page-metadata">', 1)[0]
    body = body.replace("</p>", " ")
    text = _TAGS.sub(" ", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _terms(text: str) -> set[str]:
    # Crude stemming ("returns" -> "return") so plurals match.
    words = (w.rstrip("s") for w in re.findall(r"[a-z0-9]+", text.lower()))
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def _search(pages: list[dict], query: str) -> list[dict]:
    """The MAX_PAGES pages best matching the query; titles count more than body."""
    wanted = _terms(query)
    scored = []
    for page in pages:
        title = _terms(page["title"])
        body = _terms(_page_text(page["html"]))
        score = 3 * len(wanted & title) + len(wanted & body)
        if score:
            scored.append((score, page))
    scored.sort(key=lambda pair: -pair[0])
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

    matches = _search(policy_export.pages(), query)
    results = [{"title": page["title"], "text": _page_text(page["html"])} for page in matches]
    payload = json.dumps({"query": query, "pages": results})

    set_tool_attribute("policy.pages", len(results))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(results)} pages, {len(payload)} bytes")

    if matches:
        session.record_widget(
            "search_policies",
            "policy",
            {"title": matches[0]["title"], "excerpt": _excerpt(matches[0]["html"])},
        )
    return payload
