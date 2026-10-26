"""Replay a captured /checkout request against the working-tree Flask code.

The cart comes from the `cart_json` attribute on the "Failed to validate inventory"
Sentry log line. Inventory is stubbed with enough stock for every item in the cart,
so a 500 here means the code is broken, not the database.

Usage (from the repo root):
    python selfheal/harness/replay.py path/to/cart.json
Prints the status and body, exits 0 on HTTP 200 and 1 otherwise.
"""
import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

FLASK_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "flask")


def load_cart(path):
    with open(path) as f:
        data = json.load(f)
    # Accept the bare cart, or a whole order body with a "cart" key
    return data["cart"] if "cart" in data else data


def replay(cart):
    sys.path.insert(0, os.path.abspath(FLASK_DIR))
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    # Reuse the test stubs for env vars, Statsig and the database
    from src.test import conftest  # noqa: F401  (sets env vars, imports the app)
    from src import main

    stock = [SimpleNamespace(id=int(pid), productid=int(pid), count=int(qty) + 100)
             for pid, qty in cart["quantities"].items()]
    order = {"cart": cart, "form": {"email": "replay@example.com"}, "validate_inventory": "true"}

    with patch.object(main, "get_inventory", return_value=stock), \
         patch.object(main, "decrement_inventory"), \
         patch.object(main, "evaluate_statsig_flags"):
        try:
            response = main.app.test_client().post(
                "/checkout", data=json.dumps(order), content_type="application/json")
        except Exception as err:
            # The test client re-raises unhandled errors; in production they're a 500
            cause = f" (caused by {err.__cause__!r})" if err.__cause__ else ""
            return 500, f"{err!r}{cause}"
    return response.status_code, response.get_data(as_text=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    status, body = replay(load_cart(sys.argv[1]))
    print(json.dumps({"status": status, "body": body}))
    sys.exit(0 if status == 200 else 1)
