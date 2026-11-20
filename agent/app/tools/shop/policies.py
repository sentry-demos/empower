"""Store policy lookup, backed by a mock help-centre export.

search_policies ranks the export's pages against the query and returns only the
best few, as plain text. checkout_agent stops on its first tool, so this result
becomes the delegation's result verbatim and lands in the orchestrator's next
gen_ai.chat call; it has to stay small. policy.pages and policy.bytes on the
tool span record what was returned.
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

# Pages handed to the model per search.
MAX_PAGES = 3

_STOPWORDS = {
    "a", "an", "the", "to", "of", "for", "is", "are", "do", "does", "you",
    "your", "what", "how", "can", "i", "my", "me", "we", "our", "and", "or",
    "in", "on", "it", "about", "have", "any", "there",
}


def _body_text(html: str) -> str:
    """A page's body copy, without the export's chrome or markup."""
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
    """Lower-cased words minus stopwords, with a trailing 's' dropped."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w[:-1] if len(w) > 3 and w.endswith("s") else w
            for w in words if w not in _STOPWORDS}


def _rank(query: str, pages: list[dict]) -> list[dict]:
    """Pages that share words with the query, best match first."""
    wanted = _terms(query)
    scored = []
    for page in pages:
        title_hits = len(wanted & _terms(page["title"]))
        body_hits = len(wanted & _terms(_body_text(page["html"])))
        score = 3 * title_hits + body_hits
        if score:
            scored.append((score, page))
    scored.sort(key=lambda s: -s[0])  # stable: ties keep export order
    return [page for _, page in scored]


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

    matches = _rank(query, policy_export.pages())[:MAX_PAGES]
    payload = json.dumps(
        {
            "query": query,
            "pages": [
                {"title": page["title"], "text": _body_text(page["html"])}
                for page in matches
            ],
        }
    )

    set_tool_attribute("policy.pages", len(matches))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(matches)} pages, {len(payload)} bytes")

    if matches:
        answer = matches[0]
        session.record_widget(
            "search_policies",
            "policy",
            {"title": answer["title"], "excerpt": _excerpt(answer["html"])},
        )
    return payload
