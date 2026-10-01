"""SSE protocol for POST /api/v1/chat.

The widget needs three things off a turn that a single JSON response can't give
it: progress while a slow tool runs, prose as it's generated, and structured
payloads to render as cards. So each turn is a short event stream:

    status       {tool, label, agent}   "Searching products…" ticker
    token        {text}                 streaming assistant prose
    message_end  {agent}                closes the current prose bubble
    agent_end    {tool, agent, ran}     a specialist finished (or never started)
    widget  {type, tool, data, agent}   product list / cart / checkout / error card
    pills   {pills:[{id,label}]}        suggestion chips
    done    {conversation_id}           ends the turn
    error   {code, message}             error bubble

`agent` is `{id, name}` and says who did the work, so the transcript can show
"Plant Agent ran" against the card that agent produced. It is on four of the
events rather than one because the answer differs per event: a card's author is
the specialist that ran nested, while the prose right below it was written by
the orchestrator.
"""

import json
import logging
from typing import Any, AsyncIterator

from agents import Runner
from agents.stream_events import RunItemStreamEvent

from ..agents.shopping_agent import SHOPPING_AGENT_NAME, shopping_agent
from ..session import ChatSession
from ..telemetry import agent_transaction, manager_client

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Who the customer is told is doing the work. The ids are the areas the three
# Sentry projects are split along (kunal-manager-agent / kunal-plant-agent /
# kunal-shopping-agent), so a badge in the chat and a transaction in Sentry name
# the same thing — which is the point of showing them at all.
#
# Note the display names follow the projects, not the Python identifiers:
# products_agent is the "Plant Agent" and checkout_agent is the "Shopping Agent",
# while the agent *called* shopping_agent is the orchestrator and shows as the
# Manager Agent.
AGENTS = {
    "manager": "Manager Agent",
    "plant": "Plant Agent",
    "shopping": "Shopping Agent",
    "plant_expert": "Plant Expert Agent",
}

DEFAULT_AGENT = "manager"

# Tool -> the agent that runs when it is called. Both levels are here because
# attribution is needed for both: the orchestrator's delegation tools are the
# only calls visible on this stream, while the shopping tools run inside a
# nested Runner.run and reach us only as cards recorded on the session.
TOOL_AGENTS = {
    # The orchestrator's own tools.
    "ask_products_agent": "plant",
    "ask_checkout_agent": "shopping",
    "transfer_to_plant_expert_agent": "plant_expert",
    # The plant expert's, which do run on this stream — it is handed off to
    # rather than delegated to, so it shares the orchestrator's run.
    "get_plant_basic_info": "plant_expert",
    "get_plant_recommendations": "plant_expert",
    # The shopping tools, reached through record_widget.
    "search_products": "plant",
    "add_to_cart": "shopping",
    "view_cart": "shopping",
    "start_checkout": "shopping",
    "apply_coupon": "shopping",
    "purchase": "shopping",
}

# SDK agent name -> agent id, for whoever is speaking. Only the orchestrator and
# the plant expert ever produce a message on this stream; a specialist's prose is
# the return value of a delegation, not a message.
SPEAKER_AGENTS = {
    "shopping_agent": "manager",
    "plant_expert_agent": "plant_expert",
    "products_agent": "plant",
    "checkout_agent": "shopping",
}

# Delegation tool -> the key ask_*_agent claims in session.delegations_this_turn.
#
# A second delegation in one turn is refused there (see shopping_agent.py) and
# the refusal is invisible on this stream: the tool was still *called*, so it
# still announced itself. Without this check the transcript would credit a
# specialist for work it was stopped from doing.
DELEGATION_CLAIMS = {
    "ask_products_agent": "products_agent",
    "ask_checkout_agent": "checkout_agent",
}

# Shown while a tool runs, keyed by the tool the orchestrator called. Only the
# orchestrator's own tools appear on this stream: the shopping tools belong to
# sub-agents now, and a sub-agent's nested Runner.run emits no events here — so
# the ticker is per-specialist rather than per-tool. The transfer_to_* entry is
# the SDK's generated handoff tool, which arrives as handoff_requested rather
# than tool_called — see stream_turn.
STATUS_LABELS = {
    "ask_products_agent": "Checking the catalogue…",
    "ask_checkout_agent": "Working on your order…",
    "transfer_to_plant_expert_agent": "Asking our plant expert…",
    "get_plant_basic_info": "Looking up the plant…",
    "get_plant_recommendations": "Finding a good match…",
}

# Shopping tools that move the flow along, and the card each one produces. The
# tools themselves record these on the session (ChatSession.record_widget); this
# is here so pills_for() knows which names count as flow steps.
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


def agent_ref(agent_id: str | None) -> dict[str, str]:
    """`{id, name}` for an agent, as the widget renders it.

    Falls back to the orchestrator rather than raising: an unmapped tool is a
    missing TOOL_AGENTS entry, and losing a badge is a better failure than
    losing the turn.
    """
    if agent_id not in AGENTS:
        agent_id = DEFAULT_AGENT
    return {"id": agent_id, "name": AGENTS[agent_id]}


def _tool_name(raw_item: Any) -> str | None:
    """Tool name off a tool-call raw item, whichever shape the model produced."""
    if isinstance(raw_item, dict):
        return raw_item.get("name")
    return getattr(raw_item, "name", None)


def _call_id(raw_item: Any) -> str | None:
    """Call id off a tool call or its output, so the two can be paired up.

    A tool_output item carries the call_id but not the tool's name, and the name
    is what says which agent just finished.
    """
    if isinstance(raw_item, dict):
        return raw_item.get("call_id")
    return getattr(raw_item, "call_id", None)


async def stream_turn(session: ChatSession, message: str) -> AsyncIterator[str]:
    """Run one conversational turn, yielding SSE frames as it goes."""
    turn_input = session.history + [{"role": "user", "content": message}]
    # Clears leftovers from a turn that failed part-way, and re-arms the
    # one-delegation-per-turn claim the orchestrator's tools check.
    session.begin_turn()

    # Tools already announced this turn. The orchestrator sometimes attempts a
    # second delegation, which ask_*_agent refuses (see session.claim_delegation)
    # — but the attempt still surfaces as a tool_called event, and showing
    # "Working on your order…" twice suggests work that never happened.
    announced: set[str] = set()

    # call_id -> tool name, so a tool_output can be traced back to what ran.
    calls: dict[str, str] = {}

    # Who is talking. The SDK announces the starting agent before anything else
    # and again on every handoff, so this is only ever wrong if that stops.
    speaker = DEFAULT_AGENT

    try:
        # The orchestrator's own turn, in its own project. Two reasons it has to
        # wrap the drain and not just the run_streamed call: the run happens in a
        # task created here, which is what puts its gen_ai.* spans on this
        # client, and leaving the block ends the transaction — the spans would
        # have nothing open to attach to. The specialists' routed transactions
        # read their trace headers off this scope, so they nest under this one
        # rather than under the http.server transaction.
        with agent_transaction(manager_client(), SHOPPING_AGENT_NAME):
            result = Runner.run_streamed(
                shopping_agent, input=turn_input, context=session
            )

            async for event in result.stream_events():
                if event.type == "raw_response_event":
                    kind = getattr(event.data, "type", None)
                    if kind == "response.output_text.delta":
                        # In chat_completions mode most chunks carry an empty delta
                        # (role, tool-call arguments, finish); only ~7% are prose.
                        # Don't spend an SSE frame on the rest.
                        if event.data.delta:
                            yield sse("token", {"text": event.data.delta})
                    continue

                if event.type == "agent_updated_stream_event":
                    speaker = SPEAKER_AGENTS.get(event.new_agent.name, DEFAULT_AGENT)
                    continue

                if not isinstance(event, RunItemStreamEvent):
                    continue

                # A handoff is a tool call to the model but not to the SDK, which
                # routes HandoffCallItem to handoff_requested and never to
                # tool_called. Handling only the latter is why the plant expert has
                # been running without ever announcing itself.
                if event.name in ("tool_called", "handoff_requested"):
                    name = _tool_name(event.item.raw_item)
                    if name is None:
                        continue
                    call_id = _call_id(event.item.raw_item)
                    if call_id:
                        # Recorded before the dedup below: a second call to the same
                        # tool is not worth announcing again, but its output still
                        # has to resolve to a name.
                        calls[call_id] = name
                    if name in announced:
                        continue
                    announced.add(name)
                    yield sse(
                        "status",
                        {
                            "tool": name,
                            "label": STATUS_LABELS.get(name, "Working…"),
                            "agent": agent_ref(TOOL_AGENTS.get(name)),
                        },
                    )

                elif event.name == "message_output_created":
                    # A turn can produce several assistant messages back to back.
                    # Without this the widget appends them all to one bubble and the
                    # sentences run together ("...checkout?Would you like...").
                    #
                    # The speaker rides along because it is not always the
                    # orchestrator: after a handoff the prose is the plant expert's.
                    yield sse("message_end", {"agent": agent_ref(speaker)})

                elif event.name == "tool_output":
                    # Cards come off the session rather than this event's payload:
                    # the tool that produced them ran inside a sub-agent's nested
                    # Runner.run, whose own tool events never reach this stream. A
                    # delegation can produce more than one card, so drain them all.
                    #
                    # Each card names the tool that recorded it, which is how a card
                    # gets attributed to the specialist that actually built it rather
                    # than to whoever the last status event happened to mention.
                    for widget in session.drain_widgets():
                        agent = agent_ref(TOOL_AGENTS.get(widget.get("tool")))
                        yield sse("widget", {**widget, "agent": agent})

                    name = calls.get(_call_id(event.item.raw_item) or "")
                    if name:
                        # Whether the specialist ran at all, not just whether it was
                        # asked to — see DELEGATION_CLAIMS. A tool with no claim to
                        # make (the plant expert's) always counts as having run.
                        claim = DELEGATION_CLAIMS.get(name)
                        ran = claim is None or claim in session.delegations_this_turn
                        yield sse(
                            "agent_end",
                            {
                                "tool": name,
                                "agent": agent_ref(TOOL_AGENTS.get(name)),
                                "ran": ran,
                            },
                        )

            # Carry the conversation forward. to_input_list() merges this turn's
            # input with everything the run generated, which is what the next turn
            # needs to see — minus the superseded tool JSON that remember() drops.
            session.remember(result.to_input_list())

            yield sse("pills", {"pills": pills_for(session.last_tool)})

    except Exception as error:
        # Headers are already on the wire by the time anything in here can fail,
        # so a turn-level failure has to be reported in-band as an event rather
        # than as an HTTP status.
        logging.exception("chat turn failed")
        yield sse("widget", {"type": "error", "data": {"message": str(error)}})
        yield sse("error", {"code": "turn_failed", "message": str(error)})

    yield sse("done", {"conversation_id": session.conversation_id})
