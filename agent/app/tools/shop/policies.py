"""Store policy lookup, backed by a mock help-centre export.

search_policies returns only the few pages that match the customer's question,
as plain text. checkout_agent stops on its first tool, so this output becomes
the delegation's result verbatim and lands in the orchestrator's next
gen_ai.chat call. Returning the whole export as raw HTML (~160KB) used to cost
~48k input tokens per policy question.
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

_WORDS = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    "a an and are can do does for how i in is it me my of on or the to what "
    "when where which with you your".split()
)


def _body_text(html: str) -> str:
    """A page's body copy, without the export's markup and page chrome."""
    body = html.split('class="wiki-content"', 1)[-1]
    # The body ends at the wiki-content div's close, which follows any nested divs.
    body = body.split("</h1>", 1)[-1].split('<div class="page-metadata">', 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    return _body_text(html)[:EXCERPT_CHARS]


def _terms(text: str) -> set[str]:
    """Lower-cased words with a crude plural strip, so "return" matches "returns"."""
    return {
        w[:-1] if len(w) > 3 and w.endswith("s") else w
        for w in _WORDS.findall(text.lower())
        if w not in _STOPWORDS
    }


def _search(query: str, pages: list[dict]) -> list[dict]:
    """The pages that best match the query, as plain text, best first."""
    wanted = _terms(query)
    scored = []
    for page in pages:
        text = _body_text(page["html"])
        title_hits = len(wanted & _terms(page["title"]))
        body_hits = len(wanted & _terms(text))
        score = 3 * title_hits + body_hits
        if score:
            scored.append((score, page, text))
    scored.sort(key=lambda s: -s[0])  # stable: ties keep export order
    return [
        {"id": p["id"], "title": p["title"], "text": t}
        for _, p, t in scored[:MAX_PAGES]
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

    matches = _search(query, policy_export.pages())
    payload = json.dumps({"query": query, "pages": matches})

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
