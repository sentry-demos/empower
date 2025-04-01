import unittest
import json
from unittest.mock import patch, MagicMock
from src.main import app


class TestCheckout(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('src.main.get_inventory')
    def test_checkout_insufficient_inventory(self, mock_get_inventory):
        # Mock inventory response - Product ID 3 has only 1 item in stock
        mock_get_inventory.return_value = [[1, 'asyqtzmrhsabqxri', 1, 3]]
        
        # Request 3 units of Product ID 3
        test_data = {
            "cart": {
                "items": [
                    {
                        "id": 3,
                        "title": "Plant Mood",
                        "price": 155
                    }
                ],
                "quantities": {
                    "3": 3
                },
                "total": 465
            },
            "form": {
                "name": "Test User",
                "email": "test@example.com"
            }
        }
        
        response = self.app.post('/checkout', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Checkout should fail with a detailed error message
        self.assertEqual(response.status_code, 500)
        self.assertIn("Not enough inventory for product ID 3", response.data.decode())

    @patch('src.main.get_inventory')
    def test_checkout_product_not_in_inventory(self, mock_get_inventory):
        # Mock inventory response - Product ID 3 is not in inventory
        mock_get_inventory.return_value = [[1, 'asyqtzmrhsabqxri', 5, 4]]
        
        # Request Product ID 3 which doesn't exist in inventory
        test_data = {
            "cart": {
                "items": [
                    {
                        "id": 3,
                        "title": "Plant Mood",
                        "price": 155
                    }
                ],
                "quantities": {
                    "3": 2
                },
                "total": 310
            },
            "form": {
                "name": "Test User",
                "email": "test@example.com"
            }
        }
        
        response = self.app.post('/checkout', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Checkout should fail with a product not found error
        self.assertEqual(response.status_code, 500)
        self.assertIn("Product ID 3 not found in inventory", response.data.decode())

    @patch('src.main.get_inventory')
    def test_checkout_successful(self, mock_get_inventory):
        # Mock inventory response - Product ID 3 has 5 items in stock
        mock_get_inventory.return_value = [[1, 'asyqtzmrhsabqxri', 5, 3]]
        
        # Request 3 units of Product ID 3
        test_data = {
            "cart": {
                "items": [
                    {
                        "id": 3,
                        "title": "Plant Mood",
                        "price": 155
                    }
                ],
                "quantities": {
                    "3": 3
                },
                "total": 465
            },
            "form": {
                "name": "Test User",
                "email": "test@example.com"
            }
        }
        
        response = self.app.post('/checkout', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Checkout should succeed
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "success")

    @patch('src.main.get_inventory')
    def test_checkout_no_products_selected(self, mock_get_inventory):
        # Mock empty inventory response
        mock_get_inventory.return_value = []
        
        # Empty cart
        test_data = {
            "cart": {
                "items": [],
                "quantities": {},
                "total": 0
            },
            "form": {
                "name": "Test User",
                "email": "test@example.com"
            }
        }
        
        response = self.app.post('/checkout', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Checkout should fail with no products selected error
        self.assertEqual(response.status_code, 500)
        self.assertIn("No products selected for checkout", response.data.decode())