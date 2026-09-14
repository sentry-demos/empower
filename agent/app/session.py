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

# Long enough for a user to read a product list and decide, short enough that
# abandoned demo conversations don't accumulate.
SESSION_TTL_SECONDS = 30 * 60

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
    last_seen: float = field(default_factory=time.monotonic)

    def begin_turn(self) -> None:
        """Reset per-turn state. Anything left over isn't this turn's."""
        self.pending_widgets = []
        self.delegations_this_turn = set()

    def claim_delegation(self, specialist: str) -> bool:
        """Claim the turn's single delegation. False if it is already taken."""
        if self.delegations_this_turn:
            return False
        self.delegations_this_turn.add(specialist)
        return True

    def record_widget(self, tool: str, widget_type: str, data: Any) -> None:
        """Note that `tool` ran and queue a card for the widget to render."""
        self.last_tool = tool
        self.pending_widgets.append({"type": widget_type, "data": data})

    def drain_widgets(self) -> list[dict[str, Any]]:
        """Take everything queued since the last drain."""
        widgets, self.pending_widgets = self.pending_widgets, []
        return widgets

    def add_items(self, items: list[dict[str, Any]], quantities: dict[int, int]) -> None:
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
