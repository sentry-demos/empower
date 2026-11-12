"""Store policy lookup, backed by a mock help-centre export.

This is the context snowball in the demo. search_policies is meant to find the
page that answers the customer's question, but it ignores the query and returns
every page of the export as raw HTML — about 160KB. checkout_agent stops on its
first tool, so that blob becomes the delegation's result verbatim and lands in
the orchestrator's next gen_ai.chat call as tens of thousands of input tokens.

The answer the customer gets is right, and nothing errors. The only sign is the
input token count on that one span, with policy.pages and policy.bytes on the
tool span above it saying where it came from.

The fix (strip the markup, return only the pages that match the query) is left
for Seer to propose, so the tests pin the broken behaviour down on purpose.
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


def _excerpt(html: str) -> str:
    """The first EXCERPT_CHARS of a page's body copy, without markup."""
    body = html.split('class="wiki-content"', 1)[-1]
    body = body.split("</h1>", 1)[-1].split("</div>", 1)[0]
    # Paragraph breaks become spaces, or "number.</p><p>Once" reads "number.Once".
    body = body.replace("</p>", " ")
    text = _TAGS.sub("", body).replace("&ndash;", "–").replace("&amp;", "&")
    return " ".join(text.split())[:EXCERPT_CHARS]


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

    # The bug: every page, raw, whatever was asked.
    pages = policy_export.pages()
    payload = json.dumps({"query": query, "pages": pages})

    set_tool_attribute("policy.pages", len(pages))
    set_tool_attribute("policy.bytes", len(payload))
    logging.info(f"search_policies returned {len(pages)} pages, {len(payload)} bytes")

    answer = next(
        page for page in pages if page["title"] == policy_export.RETURNS_PAGE_TITLE
    )
    session.record_widget(
        "search_policies",
        "policy",
        {"title": answer["title"], "excerpt": _excerpt(answer["html"])},
    )
    return payload
