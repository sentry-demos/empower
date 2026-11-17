"""Store policy lookup, backed by a mock help-centre export.

search_policies returns only the few pages that match the customer's query, as
plain text. checkout_agent stops on its first tool, so this result becomes the
delegation's result verbatim and lands in the orchestrator's next gen_ai.chat
call; it must stay small (it once returned the whole raw-HTML export, ~160KB).
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


def _excerpt(html: str, limit: int | None = EXCERPT_CHARS) -> str:
    """A page's body copy without markup, cut to `limit` characters if given."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split("</div>", 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())[:limit]


MAX_PAGES = 3
_WORDS = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "do", "does", "for", "how", "i", "in", "is", "it",
    "me", "my", "of", "on", "the", "to", "what", "whats", "you", "your",
}  # fmt: skip


def _stem(word: str) -> str:
    for suffix in ("ing", "es", "s", "ed"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _stems(text: str) -> set[str]:
    return {_stem(w) for w in _WORDS.findall(text.lower()) if w not in _STOPWORDS}


def find_pages(query: str) -> list[dict[str, str]]:
    """The best-matching pages for the query as plain text, best first.

    A query word in a page title counts more than one in the body. Pages with
    no matching word are left out.
    """
    wanted = _stems(query)
    scored = []
    for page in policy_export.pages():
        text = _excerpt(page["html"], limit=None)
        score = 3 * len(wanted & _stems(page["title"])) + len(wanted & _stems(text))
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

    pages = find_pages(query)
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
