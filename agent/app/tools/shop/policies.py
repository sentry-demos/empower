"""Store policy lookup, backed by a mock help-centre export.

search_policies returns the few help-centre pages that match the customer's
question, as plain text. checkout_agent stops on its first tool, so this result
becomes the delegation's result verbatim and lands in the orchestrator's next
gen_ai.chat call; it therefore has to stay small. (It used to return every page
as raw HTML, about 160KB / 47k input tokens.)
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

# Pages returned to the model per question, and how much a title match counts
# against body mentions when ranking.
MAX_PAGES = 3
TITLE_WEIGHT = 5
_STOPWORDS = {
    "what", "whats", "the", "your", "you", "our", "are", "and", "for", "how",
    "can", "does", "do", "is", "to", "of", "a", "an", "in", "on", "with", "about",
    "policy", "policies", "tell", "me", "please",
}


def _page_text(html: str) -> str:
    """A page's body copy without the export's chrome or markup."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split('<div class="page-metadata">', 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    return _page_text(html)[:EXCERPT_CHARS]


def _match_pages(query: str, pages: list[dict]) -> list[dict]:
    """The MAX_PAGES pages that best match the query, best first.

    Pages score by how often the query's words appear in them, with title hits
    weighing more. Pages that match nothing are left out.
    """
    terms = [
        word
        for word in re.findall(r"[a-z0-9]+", query.lower())
        if word not in _STOPWORDS and len(word) > 2
    ]
    scored = []
    for page in pages:
        title = page["title"].lower()
        text = _page_text(page["html"]).lower()
        score = sum(TITLE_WEIGHT * (term in title) + text.count(term) for term in terms)
        if score:
            scored.append((score, page))
    scored.sort(key=lambda pair: -pair[0])  # stable: export order breaks ties
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

    pages = _match_pages(query, policy_export.pages())
    payload = json.dumps(
        {
            "query": query,
            "pages": [
                {"title": page["title"], "text": _page_text(page["html"])}
                for page in pages
            ],
        }
    )

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    if pages:
        session.record_widget(
            "search_policies",
            "policy",
            {"title": pages[0]["title"], "excerpt": _excerpt(pages[0]["html"])},
        )
    return payload
