"""In-memory chat session store for the conversational shopping flow.

Sessions are keyed by the `x-conversation-id` header the widget sends, and hold
the agent's own cart and checkout state so tool calls mutate something real
instead of returning canned text.

The store is process-local on purpose: agent/deploy_project.sh pins
`--min-instances 1 --max-instances 1`, so there is exactly one instance and no
cross-instance state to reconcile. If the agent ever scales past one instance
this needs to move to Redis (flask/ already talks to one).
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from .telemetry import mark_tool_error

# Long enough for a user to read a product list and decide, short enough that
# abandoned demo conversations don't accumulate.
SESSION_TTL_SECONDS = 30 * 60

# How many of the conversation's most recent tool results to carry forward in
# full. One delegation per turn (see delegations_this_turn), so this is "the
# turn just gone".
TOOL_RESULTS_KEPT = 1

# Replaces the body of a superseded tool result. Says the work happened and that
# the customer has seen it, which is all the orchestrator needs to know: it
# routes and writes one sentence, and the specialist it delegates to is briefed
# from live session state by _checkout_context rather than from this history.
OMITTED_TOOL_RESULT = (
    "[{tool} ran earlier in this conversation and the customer has already seen"
    " the result. It is omitted here; do not repeat or summarise it.]"
)


def trim_tool_outputs(history: list[Any], keep: int = TOOL_RESULTS_KEPT) -> list[Any]:
    """Collapse all but the most recent tool results down to a one-line note.

    Every turn appends its delegation's raw JSON to the history — a product
    search is ~1.3KB, a cart ~1.5KB, a checkout ~1.7KB, against ~600B for all
    of that turn's prose put together. Left alone it is re-sent to the model on
    every subsequent turn, so a demo conversation pays for its whole past on
    each new message, and `test_ai_agent.py`'s already-reduced VOLUME_FACTOR
    pays it on every synthetic run.

    The items themselves are kept, only their `output` is replaced: a
    function_call whose function_call_output has gone missing is rejected by the
    API, so this has to thin the history rather than shorten it.
    """
    # call_id -> tool name, so a collapsed result can still say what ran.
    tool_names = {
        item["call_id"]: item.get("name")
        for item in history
        if isinstance(item, dict)
        and item.get("type") == "function_call"
        and item.get("call_id")
    }

    positions = [
        index
        for index, item in enumerate(history)
        if isinstance(item, dict) and item.get("type") == "function_call_output"
    ]
    # Not positions[:-keep] — keep=0 would slice to [] and trim nothing, since
    # -0 == 0.
    superseded = set(positions[:-keep] if keep else positions)

    trimmed = []
    for index, item in enumerate(history):
        if index in superseded:
            tool = tool_names.get(item.get("call_id")) or "A specialist"
            note = OMITTED_TOOL_RESULT.format(tool=tool)
            # Not every tool result is a big JSON blob — a failed coupon or a
            # rejected purchase is a sentence, and is shorter than the note
            # explaining its absence. Collapsing those would grow the history
            # and lose detail, so leave anything already smaller alone.
            if len(note) < len(str(item.get("output", ""))):
                # Copied rather than mutated: these items came out of the SDK's
                # run result and are not ours to edit in place.
                item = {**item, "output": note}
        trimmed.append(item)

    return trimmed


# Prefilled checkout defaults, matching the non-TDA branch of
# react/src/components/CheckoutForm.jsx.
DEFAULT_FORM: dict[str, str] = {
    "email": "plant.lover@example.com",
    "subscribe": "",
    "firstName": "Jane",
    "lastName": "Greenthumb",
    "address": "123 Main Street",
    "city": "San Francisco",
    "country": "United States of America",
    "state": "CA",
    "zipCode": "94122",
    "promoCode": "SAVE20",
}


def empty_cart() -> dict[str, Any]:
    """Return an empty cart in the shape react/src/reducers/index.js produces."""
    return {"items": [], "quantities": {}, "total": 0}


@dataclass
class ChatSession:
    """One conversation's worth of agent state."""

    conversation_id: str
    # Runner input items, carried across turns via result.to_input_list().
    history: list[Any] = field(default_factory=list)
    cart: dict[str, Any] = field(default_factory=empty_cart)
    # Trimmed products from the last search_products call, so add_to_cart can
    # resolve a product id the model quotes back at us.
    last_results: list[dict[str, Any]] = field(default_factory=list)
    promo: dict[str, Any] | None = None
    form: dict[str, str] | None = None
    # Name of the last shopping tool that ran. The route layer derives the
    # suggestion pills from this rather than asking the LLM for them.
    last_tool: str | None = None
    # Cards produced by tools during the current turn, waiting to be sent.
    #
    # The shopping tools belong to sub-agents now, and a sub-agent runs in its
    # own nested Runner.run whose tool events never reach the outer stream. So
    # tools record what they want rendered here and the route drains it when the
    # delegating tool returns, rather than the route reading tool names off
    # stream events.
    pending_widgets: list[dict[str, Any]] = field(default_factory=list)
    # Specialists already delegated to during the current turn.
    #
    # One customer message must produce at most one shopping action. The
    # orchestrator's instructions say so, but instructions are advisory: it has
    # been observed calling ask_checkout_agent three times for one message,
    # applying the expired coupon three times over. This makes the rule
    # structural instead.
    delegations_this_turn: set[str] = field(default_factory=set)
    # This turn's tool failure, waiting to be read by the delegating tool. See
    # record_tool_error.
    tool_error: tuple[str, str] | None = None
    last_seen: float = field(default_factory=time.monotonic)

    def begin_turn(self) -> None:
        """Reset per-turn state. Anything left over isn't this turn's."""
        self.pending_widgets = []
        self.delegations_this_turn = set()
        self.tool_error = None

    def remember(self, history: list[Any]) -> None:
        """Carry a finished turn's history into the next one.

        Goes through trim_tool_outputs rather than storing the run's input list
        as-is, so the conversation's prose accumulates but its tool JSON does
        not.
        """
        self.history = trim_tool_outputs(history)

    def claim_delegation(self, specialist: str) -> bool:
        """Claim the turn's single delegation. False if it is already taken."""
        if self.delegations_this_turn:
            return False
        self.delegations_this_turn.add(specialist)
        return True

    def record_widget(self, tool: str, widget_type: str, data: Any) -> None:
        """Note that `tool` ran and queue a card for the widget to render."""
        self.last_tool = tool
        # The tool name travels with the card. The route needs it to say which
        # agent produced this card, and it cannot work that out from the stream:
        # the only tool call it saw was the orchestrator's delegation, which is
        # a level above the tool that actually built this.
        self.pending_widgets.append({"type": widget_type, "tool": tool, "data": data})

    def record_tool_error(self, error_type: str, message: str) -> None:
        """Fail this tool's span, and hand the failure to the delegating tool.

        Two execute_tool spans house a shopping failure: the tool's own, in the
        specialist's project, and the orchestrator's delegation span one level
        up, in the manager's. Only the first is reachable from inside the tool —
        the second belongs to the outer scope ask_checkout_agent runs in — so
        the failure rides up on the session and is marked there.
        """
        mark_tool_error(error_type, message)
        self.tool_error = (error_type, message)

    def take_tool_error(self) -> tuple[str, str] | None:
        """Take the failure recorded by this turn's tool, if there was one."""
        error, self.tool_error = self.tool_error, None
        return error

    def drain_widgets(self) -> list[dict[str, Any]]:
        """Take everything queued since the last drain."""
        widgets, self.pending_widgets = self.pending_widgets, []
        return widgets

    def add_items(
        self, items: list[dict[str, Any]], quantities: dict[int, int]
    ) -> None:
        """Merge products into the cart, mirroring the ADD_PRODUCT reducer."""
        by_id = {item["id"]: item for item in self.cart["items"]}
        for product in items:
            if product["id"] not in by_id:
                self.cart["items"].append(product)
                by_id[product["id"]] = product

        for product_id, qty in quantities.items():
            # Flask reads cart['quantities'] keys back through int(), but the
            # Redux cart has string keys because it came from JSON. Keep strings
            # so /checkout sees the same shape either flow produces.
            key = str(product_id)
            self.cart["quantities"][key] = self.cart["quantities"].get(key, 0) + qty

        self.recalculate_total()

    def recalculate_total(self) -> None:
        """Recompute cart total as sum(price * quantity), as the reducer does."""
        total = 0.0
        for product in self.cart["items"]:
            qty = self.cart["quantities"].get(str(product["id"]), 0)
            total += product.get("price", 0) * qty
        total = round(total, 2)
        # Keep whole totals as ints, like the Redux reducer's integer maths. The
        # cart and checkout cards render `${total}.00`, so a stray float would
        # show up as "$510.0.00".
        self.cart["total"] = int(total) if total == int(total) else total


_sessions: dict[str, ChatSession] = {}
_lock = threading.Lock()


def get_session(conversation_id: str) -> ChatSession:
    """Fetch (or create) the session for a conversation id, sweeping stale ones."""
    now = time.monotonic()
    with _lock:
        for stale_id in [
            key
            for key, session in _sessions.items()
            if now - session.last_seen > SESSION_TTL_SECONDS
        ]:
            del _sessions[stale_id]

        session = _sessions.get(conversation_id)
        if session is None:
            session = ChatSession(conversation_id=conversation_id)
            _sessions[conversation_id] = session

        session.last_seen = now
        return session
