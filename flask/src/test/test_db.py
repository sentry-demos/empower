"""DB access tests with the database connection stubbed out."""
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src import db


class Row(dict):
    """Row that supports both dict() conversion and attribute access, like a SQLAlchemy row."""
    __getattr__ = dict.__getitem__


def test_get_products_fetches_reviews_in_one_query():
    # Regression for the N+1 query: reviews used to be queried once per product.
    products = [Row(id=1, name="a"), Row(id=2, name="b"), Row(id=3, name="c")]
    reviews = [
        Row(id=10, productid=1, rating=5),
        Row(id=11, productid=3, rating=4),
        Row(id=12, productid=1, rating=3),
    ]
    executed = []

    def execute(query, **params):
        executed.append(str(query))
        rows = products if "FROM products" in str(query) else reviews
        return SimpleNamespace(fetchall=lambda: rows)

    connection = MagicMock()
    connection.execute.side_effect = execute

    with patch.object(db.db, "connect", return_value=connection), patch.object(db, "weighter", return_value=0):
        result = json.loads(db.get_products())

    assert len(executed) == 2  # one for products, one for all reviews
    by_id = {p["id"]: [r["id"] for r in p["reviews"]] for p in result}
    assert by_id == {1: [10, 12], 2: [], 3: [11]}
