"""Store policy lookup, backed by a mock help-centre export.

search_policies returns only the few pages that match the customer's query, as
plain text with the export's markup stripped. checkout_agent stops on its first
tool, so this output becomes the delegation's result verbatim and lands in the
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


MAX_RESULTS = 3
_WORDS = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is",
    "me", "my", "of", "on", "or", "the", "to", "what", "your", "you", "about",
}


def _body_text(html: str) -> str:
    """A page's body copy without the export's markup."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split('<div class="page-metadata">', 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _search(query: str) -> list[dict[str, str]]:
    """The best-matching pages (title and plain text), most relevant first."""
    terms = [t for t in _WORDS.findall(query.lower()) if t not in _STOPWORDS]
    scored = []
    for page in policy_export.pages():
        text = _body_text(page["html"])
        title = page["title"].lower()
        body = text.lower()
        # A query word matches a longer word that starts with it ("return" ~ "returns").
        score = sum(3 * (t in title) + (t in body) for t in terms)
        if score:
            scored.append((score, {"title": page["title"], "html": page["html"], "text": text}))
    scored.sort(key=lambda s: -s[0])
    return [page for _, page in scored[:MAX_RESULTS]]


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
    payload = json.dumps(
        {
            "query": query,
            "pages": [{"title": m["title"], "text": m["text"]} for m in matches],
        }
    )

    set_tool_attribute("policy.pages", len(matches))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(matches)} pages, {len(payload)} bytes")

    if matches:
        best = matches[0]
        session.record_widget(
            "search_policies",
            "policy",
            {"title": best["title"], "excerpt": best["text"][:EXCERPT_CHARS]},
        )
    return payload
