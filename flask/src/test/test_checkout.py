"""/checkout tests."""
import json

from .conftest import make_order


def post_checkout(client, order):
    return client.post("/checkout", data=json.dumps(order), content_type="application/json")


def test_checkout_without_inventory_validation_succeeds(client, inventory):
    inventory.stock.update({3: 10})

    response = post_checkout(client, make_order({3: 1}, validate_inventory="false"))

    assert response.status_code == 200
    assert json.loads(response.data) == {"status": "success"}
    assert inventory.decrements == []


def test_checkout_with_inventory_validation_succeeds(client, inventory):
    # Regression: `quantities` was read before it was assigned, so every validated checkout raised
    # UnboundLocalError and surfaced as "Error validating enough inventory for product".
    inventory.stock.update({4: 5})

    response = post_checkout(client, make_order({4: 1}))

    assert response.status_code == 200
    assert json.loads(response.data) == {"status": "success"}
    assert inventory.decrements == [(4, 1)]
