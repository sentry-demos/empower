import pytest

from src.cart_utils import CartValidationError, normalize_quantities, resolve_item_title


def test_normalize_quantities_casts_keys_and_values():
    cart = {"quantities": {"1": "2", 3: 4}}

    result = normalize_quantities(cart)

    assert result == {1: 2, 3: 4}


@pytest.mark.parametrize(
    "cart_payload",
    [
        {},
        {"quantities": {}},
        {"quantities": []},
    ],
)
def test_normalize_quantities_raises_for_empty_or_invalid_payload(cart_payload):
    with pytest.raises(CartValidationError):
        normalize_quantities(cart_payload)


def test_resolve_item_title_prefers_title_then_name_then_fallback():
    items = [
        {"id": 1, "title": "Fancy Plant"},
        {"id": 2, "name": "Backup Name"},
    ]

    assert resolve_item_title(items, 1) == "Fancy Plant"
    assert resolve_item_title(items, 2) == "Backup Name"
    assert resolve_item_title(items, 3) == "Product 3"
