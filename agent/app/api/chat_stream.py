"""SSE protocol for POST /api/v1/chat.

The widget needs three things off a turn that a single JSON response can't give
it: progress while a slow tool runs, prose as it's generated, and structured
payloads to render as cards. So each turn is a short event stream:

    status       {tool, label}    "Searching products…" ticker
    token        {text}           streaming assistant prose
    message_end  {}               closes the current prose bubble
    widget  {type, data}          product list / cart / checkout / error card
    pills   {pills:[{id,label}]}  suggestion chips
    done    {conversation_id}     ends the turn
    error   {code, message}       error bubble
"""

import json
import logging
from typing import Any, AsyncIterator

from agents import Runner
from agents.stream_events import RunItemStreamEvent

from ..agents.shopping_agent import shopping_agent
from ..session import ChatSession

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Shown while a tool runs. Keyed by tool name. The transfer_to_* entries are the
# SDK's generated handoff tools, which show up here like any other tool call.
STATUS_LABELS = {
    "search_products": "Searching products…",
    "add_to_cart": "Adding to cart…",
    "view_cart": "Loading cart…",
    "start_checkout": "Preparing checkout…",
    "apply_coupon": "Applying coupon…",
    "purchase": "Placing order…",
    "transfer_to_plant_expert_agent": "Asking our plant expert…",
    "get_plant_basic_info": "Looking up the plant…",
    "get_plant_recommendations": "Finding a good match…",
}

# Which card the widget should render for a given tool's output.
WIDGET_TYPES = {
    "search_products": "products",
    "add_to_cart": "cart",
    "view_cart": "cart",
    "start_checkout": "checkout",
    "apply_coupon": "promo",
    "purchase": "confirmation",
}

# Suggestion pills, keyed by the tool that last ran. Derived here rather than
# asked of the LLM: the demo needs the same four clicks to work every run, but
# the conversation itself stays a real LLM loop over whatever the user types.
# The pills are just pre-filled prompts, not the only way through the flow.
_PILLS = {
    "id": {
        "show_products": "chat-pill-show-products",
        "add_all": "chat-pill-add-all",
        "checkout": "chat-pill-checkout",
        "apply_coupon": "chat-pill-apply-coupon",
        "purchase": "chat-pill-purchase",
    }
}

# $200, not $40: the catalogue is $25/$155/$155/$175/$250, so a $40 ceiling
# returns a single product and there is nothing to render as a list or to
# "add one of each" of.
PILLS_INITIAL = [
    {"id": _PILLS["id"]["show_products"], "label": "Show me plants under $200"}
]

# Both checkout actions stay available while the customer is on that step: the
# coupon is expected to fail, so Purchase has to still be reachable after it.
PILLS_CHECKOUT = [
    {"id": _PILLS["id"]["apply_coupon"], "label": "Apply Coupon"},
    {"id": _PILLS["id"]["purchase"], "label": "Purchase"},
]

PILLS_BY_LAST_TOOL: dict[str | None, list[dict[str, str]]] = {
    None: PILLS_INITIAL,
    "search_products": [
        {"id": _PILLS["id"]["add_all"], "label": "Add one of each to the cart"}
    ],
    "add_to_cart": [{"id": _PILLS["id"]["checkout"], "label": "Checkout"}],
    "view_cart": [{"id": _PILLS["id"]["checkout"], "label": "Checkout"}],
    "start_checkout": PILLS_CHECKOUT,
    "apply_coupon": PILLS_CHECKOUT,
    # The order is the last step either way: on success the cart is emptied, on
    # failure the customer has seen the error. Offer a fresh start.
    "purchase": PILLS_INITIAL,
}


def sse(event: str, payload: dict[str, Any]) -> str:
    """Encode one Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


def pills_for(last_tool: str | None) -> list[dict[str, str]]:
    """Pills to offer after the given tool ran."""
    return PILLS_BY_LAST_TOOL.get(last_tool, PILLS_BY_LAST_TOOL[None])


def _tool_name(raw_item: Any) -> str | None:
    """Tool name off a tool-call raw item, whichever shape the model produced."""
    if isinstance(raw_item, dict):
        return raw_item.get("name")
    return getattr(raw_item, "name", None)


def _call_id(raw_item: Any) -> str | None:
    """Correlation id shared by a tool call and its output."""
    if isinstance(raw_item, dict):
        return raw_item.get("call_id")
    return getattr(raw_item, "call_id", None)


def _widget_data(output: Any) -> Any:
    """Decode a tool's return value for the widget event."""
    if isinstance(output, str):
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {"text": output}
    return output


async def stream_turn(session: ChatSession, message: str) -> AsyncIterator[str]:
    """Run one conversational turn, yielding SSE frames as it goes."""
    turn_input = session.history + [{"role": "user", "content": message}]
    # call_id -> tool name, so a tool_output event knows which card to render.
    pending_tools: dict[str, str] = {}

    try:
        result = Runner.run_streamed(shopping_agent, input=turn_input, context=session)

        async for event in result.stream_events():
            if event.type == "raw_response_event":
                if getattr(event.data, "type", None) == "response.output_text.delta":
                    # In chat_completions mode most chunks carry an empty delta
                    # (role, tool-call arguments, finish); only ~7% are prose.
                    # Don't spend an SSE frame on the rest.
                    if event.data.delta:
                        yield sse("token", {"text": event.data.delta})
                continue

            if not isinstance(event, RunItemStreamEvent):
                continue

            if event.name == "tool_called":
                name = _tool_name(event.item.raw_item)
                if name is None:
                    continue
                call_id = _call_id(event.item.raw_item)
                if call_id:
                    pending_tools[call_id] = name
                # Only shopping tools move the flow along. Handoff and plant-care
                # tools must not, or asking a care question mid-flow would reset
                # the pills to the opening suggestion and lose the user's place.
                if name in WIDGET_TYPES:
                    session.last_tool = name
                yield sse(
                    "status",
                    {"tool": name, "label": STATUS_LABELS.get(name, "Working…")},
                )

            elif event.name == "message_output_created":
                # A turn can produce several assistant messages back to back.
                # Without this the widget appends them all to one bubble and the
                # sentences run together ("...checkout?Would you like...").
                yield sse("message_end", {})

            elif event.name == "tool_output":
                call_id = _call_id(event.item.raw_item)
                name = pending_tools.pop(call_id, None) if call_id else None
                widget_type = WIDGET_TYPES.get(name or "")
                if widget_type:
                    yield sse(
                        "widget",
                        {"type": widget_type, "data": _widget_data(event.item.output)},
                    )

        # Carry the conversation forward. to_input_list() merges this turn's
        # input with everything the run generated, which is what the next turn
        # needs to see.
        session.history = result.to_input_list()

        yield sse("pills", {"pills": pills_for(session.last_tool)})

    except Exception as error:
        # Headers are already on the wire by the time anything in here can fail,
        # so a turn-level failure has to be reported in-band as an event rather
        # than as an HTTP status.
        logging.exception("chat turn failed")
        yield sse("widget", {"type": "error", "data": {"message": str(error)}})
        yield sse("error", {"code": "turn_failed", "message": str(error)})

    yield sse("done", {"conversation_id": session.conversation_id})
