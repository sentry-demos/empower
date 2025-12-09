from typing import Any, Dict, Iterable


class CartValidationError(Exception):
    """Raised when the checkout cart payload is malformed."""


def normalize_quantities(cart: Dict[str, Any]) -> Dict[int, int]:
    """
    Convert the cart quantity mapping (which may use string keys/values)
    into an integer keyed/valued dictionary and validate the payload.
    """
    raw_quantities = cart.get("quantities", {})
    if not isinstance(raw_quantities, dict):
        raise CartValidationError("Invalid checkout request: cart quantities malformed")

    try:
        quantities = {int(k): int(v) for k, v in raw_quantities.items()}
    except (TypeError, ValueError):
        raise CartValidationError("Invalid checkout request: cart quantities malformed")

    if len(quantities) == 0:
        raise CartValidationError("Invalid checkout request: cart is empty")

    return quantities


def resolve_item_title(items: Iterable[Dict[str, Any]], product_id: int) -> str:
    """
    Try to find a human-friendly name for an item in the cart payload.
    Falls back to a generic label so the UI can still surface information.
    """
    items = items or []
    for item in items:
        if item.get("id") == product_id:
            return item.get("title") or item.get("name") or f"Product {product_id}"
    return f"Product {product_id}"
