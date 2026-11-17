"""Store policy lookup, backed by a mock help-centre export.

search_policies returns only the few pages that match the customer's query, as
plain text with the export's markup stripped. checkout_agent stops on its first
tool, so this result becomes the delegation's result verbatim and lands in the
orchestrator's next gen_ai.chat call; it must stay small.
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


_WORDS = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "how", "i", "is", "it", "my",
    "of", "on", "or", "the", "to", "what", "when", "your", "you", "policy",
}  # fmt: skip
MAX_PAGES = 3


def _body_text(html: str) -> str:
    """A page's body copy (the wiki-content div), without markup."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split("</div>", 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _stems(text: str) -> set[str]:
    return {w.rstrip("s") for w in _WORDS.findall(text.lower()) if w not in _STOPWORDS}


def _matching(pages: list[dict], query: str) -> list[dict]:
    """The pages most relevant to the query, best first, at most MAX_PAGES.

    A page scores 3 per query term in its title and 1 per term in its body.
    """
    terms = _stems(query)
    scored = []
    for page in pages:
        title, body = _stems(page["title"]), _stems(_body_text(page["html"]))
        score = 3 * len(terms & title) + len(terms & body)
        if score:
            scored.append((score, page))
    scored.sort(key=lambda item: -item[0])
    return [page for _, page in scored[:MAX_PAGES]]


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    return _body_text(html)[:EXCERPT_CHARS]


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

    all_pages = policy_export.pages()
    pages = [
        {"id": page["id"], "title": page["title"], "text": _body_text(page["html"])}
        for page in _matching(all_pages, query)
    ]
    payload = json.dumps({"query": query, "pages": pages})

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    answer = next(
        page for page in all_pages if page["title"] == policy_export.RETURNS_PAGE_TITLE
    )
    session.record_widget(
        "search_policies",
        "policy",
        {"title": answer["title"], "excerpt": _excerpt(answer["html"])},
    )
    return payload
