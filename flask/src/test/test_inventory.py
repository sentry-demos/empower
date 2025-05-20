import unittest
from unittest.mock import patch, MagicMock
from flask import json

# Patch the environment variables before importing the app
@patch.dict('os.environ', {
    'RELEASE': 'test-release',
    'FLASK_APP_DSN': 'https://xxxxyyyyy@o11111.sentry.io/11111',
    'FLASK_ENV': 'test',
    'RUBY_BACKEND': 'http://test-backend',
    'RUN_SLOW_PROFILE': 'false',
})
class TestInventory(unittest.TestCase):

    @patch('src.main.get_inventory')
    def test_checkout_insufficient_inventory(self, mock_get_inventory):
        # Setup mock to return inventory with count=1 for product_id=3
        mock_get_inventory.return_value = [{
            'id': 1,
            'sku': 'asyqtzmrhsabqxri',
            'count': 1,
            'productId': 3
        }]
        
        from src.main import app  # Import here to apply patched environment variables
        
        with app.test_client() as client:
            # Create test order with quantity=4 for product_id=3
            order = {
                "cart": {
                    "quantities": {"3": 4},
                    "items": [{
                        "id": 3,
                        "title": "Plant Mood",
                        "price": 155
                    }]
                },
                "form": {
                    "firstName": "Test",
                    "lastName": "User",
                    "email": "test@example.com"
                },
                "validate_inventory": True
            }
            
            # Send POST request to /checkout
            response = client.post(
                '/checkout',
                data=json.dumps(order),
                content_type='application/json'
            )
            
            # Verify response contains expected error
            self.assertEqual(response.status_code, 500)
            self.assertIn('Not enough inventory for product', response.data.decode())
            
            # Verify get_inventory was called with correct cart
            mock_get_inventory.assert_called_once()
            cart_arg = mock_get_inventory.call_args[0][0]
            self.assertEqual(cart_arg['quantities']['3'], 4)

    @patch('src.main.get_inventory')
    def test_checkout_sufficient_inventory(self, mock_get_inventory):
        # Setup mock to return inventory with count=5 for product_id=3
        mock_get_inventory.return_value = [{
            'id': 1,
            'sku': 'asyqtzmrhsabqxri',
            'count': 5,
            'productId': 3
        }]
        
        from src.main import app
        
        with app.test_client() as client:
            # Create test order with quantity=4 for product_id=3
            order = {
                "cart": {
                    "quantities": {"3": 4},
                    "items": [{
                        "id": 3,
                        "title": "Plant Mood",
                        "price": 155
                    }]
                },
                "form": {
                    "firstName": "Test",
                    "lastName": "User",
                    "email": "test@example.com"
                },
                "validate_inventory": True
            }
            
            # Send POST request to /checkout
            response = client.post(
                '/checkout',
                data=json.dumps(order),
                content_type='application/json'
            )
            
            # Verify successful response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode(), 'success')

if __name__ == '__main__':
    unittest.main()