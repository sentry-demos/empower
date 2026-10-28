"""/checkout tests. These pass on selfheal/base, where the validate_inventory path is
intentionally broken; a fix for that path should add its own regression test here.
"""
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
    inventory.stock.update({3: 10})

    response = post_checkout(client, make_order({3: 3}))

    assert response.status_code == 200
    assert json.loads(response.data) == {"status": "success"}
    assert inventory.decrements == [(3, 3)]
