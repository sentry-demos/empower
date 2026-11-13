"""Store policy lookup, backed by a mock help-centre export.

search_policies returns only the few pages that match the query, as plain text
without the export's markup. checkout_agent stops on its first tool, so this
result becomes the delegation's result verbatim and lands in the orchestrator's
next gen_ai.chat call; returning the whole raw export (~160KB) used to cost
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


# At most this many pages go to the model.
MAX_RESULTS = 3

_WORDS = re.compile(r"[a-z0-9]+")
_STOPWORDS = {"a", "an", "the", "to", "is", "are", "of", "do", "does", "what", "your",
              "you", "i", "my", "can", "how", "for", "in", "on", "and", "or", "policy"}


def _body_text(html: str) -> str:
    """A page's body copy, without the export's markup or page chrome."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1]
    body = body.split('<div class="page-metadata">', 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    return _body_text(html)[:EXCERPT_CHARS]


def _stem(word: str) -> str:
    return word[:-1] if len(word) > 3 and word.endswith("s") else word


def _terms(text: str) -> set[str]:
    return {_stem(w) for w in _WORDS.findall(text.lower()) if w not in _STOPWORDS}


def _search(query: str, pages: list[dict]) -> list[dict]:
    """The pages that best match the query, as plain text, best first."""
    wanted = _terms(query)
    scored = []
    for page in pages:
        text = _body_text(page["html"])
        title_terms = _terms(page["title"])
        score = 3 * len(wanted & title_terms) + len(wanted & _terms(text))
        if score:
            scored.append((score, {"title": page["title"], "text": text}))
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

    export = policy_export.pages()
    matches = _search(query, export)
    payload = json.dumps({"query": query, "pages": matches})

    set_tool_attribute("policy.pages", len(matches))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(matches)} pages, {len(payload)} bytes")

    if matches:
        best = matches[0]["title"]
        answer = next(page for page in export if page["title"] == best)
        session.record_widget(
            "search_policies",
            "policy",
            {"title": answer["title"], "excerpt": _excerpt(answer["html"])},
        )
    return payload
