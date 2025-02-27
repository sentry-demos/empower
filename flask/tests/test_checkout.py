import pytest
from unittest.mock import patch, MagicMock
from src.main import checkout
from src.db import get_inventory

def test_inventory_count_access():
    """Test that inventory count is properly accessed from DB result"""
    mock_cart = {
        "quantities": {"3": "2"},
        "items": [{
            "id": "3",
            "title": "Plant Mood"
        }]
    }
    
    mock_inventory = [
        {"id": 1, "sku": "test123", "count": 1, "productid": 3}
    ]
    
    with patch('src.db.get_inventory', return_value=mock_inventory):
        with pytest.raises(Exception) as exc_info:
            checkout(mock_cart)
        assert "Not enough inventory for product" in str(exc_info.value)

def test_sufficient_inventory():
    """Test checkout succeeds with sufficient inventory"""
    mock_cart = {
        "quantities": {"3": "2"},
        "items": [{
            "id": "3",
            "title": "Plant Mood"
        }]
    }
    
    mock_inventory = [
        {"id": 1, "sku": "test123", "count": 5, "productid": 3}
    ]
    
    with patch('src.db.get_inventory', return_value=mock_inventory):
        response = checkout(mock_cart)
        assert response.get_data().decode('utf-8') == "success"

def test_inventory_type_conversion():
    """Test proper type conversion of inventory quantities"""
    mock_cart = {
        "quantities": {"3": "2"},
        "items": [{
            "id": "3",
            "title": "Plant Mood"
        }]
    }
    
    # Test with string count to ensure conversion works
    mock_inventory = [
        {"id": 1, "sku": "test123", "count": "1", "productid": 3}
    ]
    
    with patch('src.db.get_inventory', return_value=mock_inventory):
        with pytest.raises(Exception) as exc_info:
            checkout(mock_cart)
        assert "Not enough inventory for product" in str(exc_info.value)

def test_missing_inventory():
    """Test handling of products with no inventory record"""
    mock_cart = {
        "quantities": {"999": "1"},
        "items": [{
            "id": "999",
            "title": "Missing Product"
        }]
    }
    
    mock_inventory = []
    
    with patch('src.db.get_inventory', return_value=mock_inventory):
        with pytest.raises(Exception) as exc_info:
            checkout(mock_cart)
        assert "Not enough inventory for product" in str(exc_info.value)