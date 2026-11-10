"""Store policy lookup, backed by a mock help-centre export.

search_policies returns only the few pages that match the customer's question,
as plain text. checkout_agent stops on its first tool, so this result becomes
the delegation's result verbatim and lands in the orchestrator's next
gen_ai.chat call; it must stay small. policy.pages and policy.bytes on the tool
span record its size.
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


# Most pages returned to the model for one question.
MAX_RESULTS = 3

_STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "you", "your", "to", "for",
    "of", "what", "how", "can", "i", "my", "about", "and", "or", "in", "on",
}  # fmt: skip


def _body_text(html: str) -> str:
    """A page's body copy, without markup or the export's page chrome."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split("</div>", 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    return _body_text(html)[:EXCERPT_CHARS]


def _terms(query: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", query.lower())
    return [w.rstrip("s") if len(w) > 3 else w for w in words if w not in _STOPWORDS]


def _score(terms: list[str], title: str, text: str) -> int:
    title, text = title.lower(), text.lower()
    return sum(3 * (t in title) + (t in text) for t in terms)


def _search(query: str) -> list[dict]:
    """The pages that best match the query, as plain text, best first."""
    terms = _terms(query)
    scored = []
    for page in policy_export.pages():
        text = _body_text(page["html"])
        score = _score(terms, page["title"], text)
        if score:
            scored.append((score, {"title": page["title"], "text": text}))
    scored.sort(key=lambda item: -item[0])
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

    pages = _search(query)
    payload = json.dumps({"query": query, "pages": pages})

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    if pages:
        best = pages[0]
        session.record_widget(
            "search_policies",
            "policy",
            {"title": best["title"], "excerpt": best["text"][:EXCERPT_CHARS]},
        )
    return payload
