"""Shared fixtures for Flask tests. Run from the repo root: `python -m pytest flask/src/test`

Importing src.main builds the app, which needs env vars and talks to Statsig,
Postgres and Redis. Everything external is stubbed here so tests run offline;
the database is replaced per-test by the `inventory` fixture.
"""
import os
from types import SimpleNamespace
from unittest.mock import patch

import pytest

os.environ.setdefault("FLASK_RELEASE", "test")
os.environ.setdefault("FLASK_DSN", "")  # empty DSN disables the Sentry SDK
os.environ.setdefault("FLASK_ENVIRONMENT", "local")
os.environ.setdefault("BACKEND_URL_RUBYONRAILS", "http://localhost")
os.environ.setdefault("RUN_SLOW_PROFILE", "false")
os.environ.setdefault("STATSIG_SERVER_KEY", "secret-test")
os.environ.setdefault("FLASK_REDISHOST", "localhost")
os.environ.setdefault("FLASK_REDISPORT", "6379")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_DATABASE", "test")
os.environ.setdefault("DB_USERNAME", "test")
os.environ.setdefault("DB_PASSWORD", "test")

with patch("statsig.statsig.initialize"):
    from src import main


@pytest.fixture
def client():
    return main.app.test_client()


@pytest.fixture
def inventory():
    """Stub the inventory table. Returns a dict of product id -> stock count to fill in.

    get_inventory returns rows shaped like the real query (productid, count, id),
    and decrement_inventory is recorded rather than written.
    """
    stock = {}
    decrements = []

    def fake_get_inventory(cart):
        return [SimpleNamespace(id=pid, productid=pid, count=count) for pid, count in stock.items()]

    with patch.object(main, "get_inventory", side_effect=fake_get_inventory), \
         patch.object(main, "decrement_inventory", side_effect=lambda id, count: decrements.append((id, count))), \
         patch.object(main, "evaluate_statsig_flags"):
        yield SimpleNamespace(stock=stock, decrements=decrements)


def make_order(quantities, validate_inventory="true"):
    """Build a /checkout body the way CheckoutForm.jsx and the agent's purchase tool do."""
    items = [{"id": int(pid), "title": f"Plant {pid}", "price": 50} for pid in quantities]
    return {
        "cart": {
            "items": items,
            "quantities": {str(pid): qty for pid, qty in quantities.items()},
            "total": sum(50 * qty for qty in quantities.values()),
        },
        "form": {"email": "shopper@example.com"},
        # A string, not a bool: main.py compares it with == "true"
        "validate_inventory": validate_inventory,
    }
