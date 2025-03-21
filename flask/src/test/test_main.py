### Couldn't get this test to work. Leaving commented out for now.
### Requires more packages to be installed, as well as proper/more mocking

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
class TestMain(unittest.TestCase):

    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_success(self, mock_sentry, mock_get_products_join):
        # Mock data that would be returned by get_products_join
        mock_products = [
            {
                "id": 1,
                "title": "Product 1",
                "description": "Description 1",
                "reviews": [{"rating": 5}]
            },
            {
                "id": 2,
                "title": "Product 2",
                "description": "Description 2",
                "reviews": [{"rating": 4}]
            },
            {
                "id": 3,
                "title": "Product 3",
                "description": "Description 3",
                "reviews": [{"rating": 3}]
            }
        ]
        mock_get_products_join.return_value = json.dumps(mock_products)
        
        from src.main import app  # Import here to apply patched environment variables
        with app.test_client() as client:
            response = client.get('/get_specials')
            
            # Verify response status code
            self.assertEqual(response.status_code, 200)
            
            # Verify that only 2 products are returned
            response_data = json.loads(response.data)
            self.assertEqual(len(response_data), 2)
            
            # Verify the products are the first two from the original list
            self.assertEqual(response_data[0]['id'], mock_products[0]['id'])
            self.assertEqual(response_data[1]['id'], mock_products[1]['id'])
            
            # Verify Sentry metrics were called correctly
            mock_sentry.metrics.incr.assert_called_with(
                key="endpoint_call",
                value=1,
                tags={"endpoint": "/get_specials", "method": "GET"},
            )

    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_error(self, mock_sentry, mock_get_products_join):
        # Simulate a database error
        mock_get_products_join.side_effect = Exception("Database error")
        
        from src.main import app
        with app.test_client() as client:
            with self.assertRaises(Exception) as context:
                client.get('/get_specials')
            
            self.assertEqual(str(context.exception), "Database error")
            mock_sentry.capture_exception.assert_called_once()

# import unittest
# from unittest.mock import patch, MagicMock
# from flask import json

# # Patch the environment variables before importing the app
# @patch.dict('os.environ', {
#     'RELEASE': 'test-release',
#     'FLASK_APP_DSN': 'https://xxxxyyyyy@o11111.sentry.io/11111',
#     'FLASK_ENV': 'test',
#     'RUBY_BACKEND': 'http://test-backend',
#     'RUN_SLOW_PROFILE': 'false',
# })
# class TestMain(unittest.TestCase):

#     # @patch('..main.get_inventory')
#     # @patch('..main.sentry_sdk')
#     def test_checkout_success(self):
#         # mock_get_inventory.return_value = [{'count': 10, 'productId': 1}]
        
#         from ..main import app  # Import here to apply patched environment variables
#         with app.test_client() as client:
#             order = {
#                 "cart": {"quantities": {"1": 2}},
#                 "form": {"paymentMethod": "card"}
#             }
#             response = client.post('/checkout', data=json.dumps(order), content_type='application/json')
            
#             # self.assertEqual(response.status_code, 200)
#             # self.assertEqual(response.data.decode(), "success")
            
#             # mock_sentry.metrics.incr.assert_called_with(
#             #     key="endpoint_call",
#             #     value=1,
#             #     tags={"endpoint": "/checkout", "method": "POST"},
#             # )

#     # @patch('..main.get_products')
#     # @patch('..main.sentry_sdk')
#     # def test_products_success(self, mock_sentry, mock_get_products):
#     #     mock_get_products.return_value = json.dumps([{"id": 1, "description": "Product 1"}])
        
#     #     from ..main import app  # Import here to apply patched environment variables
#     #     with app.test_client() as client:
#     #         response = client.get('/products')
            
#     #         self.assertEqual(response.status_code, 200)
#     #         self.assertIn('Product 1', response.data.decode())
#     #         mock_sentry.metrics.incr.assert_called_with(
#     #             key="endpoint_call",
#     #             value=1,
#     #             tags={"endpoint": "/products", "method": "GET"},
#     #         )

#     # @patch('..main.get_products_join')
#     # @patch('..main.sentry_sdk')
#     # def test_products_join_success(self, mock_sentry, mock_get_products_join):
#     #     mock_get_products_join.return_value = json.dumps([{"id": 1, "description": "Product 1"}])
        
#     #     from ..main import app  # Import here to apply patched environment variables
#     #     with app.test_client() as client:
#     #         response = client.get('/products-join')
            
#     #         self.assertEqual(response.status_code, 200)
#     #         self.assertIn('Product 1', response.data.decode())
#     #         mock_sentry.metrics.incr.assert_called_with(
#     #             key="endpoint_call",
#     #             value=1,
#     #             tags={"endpoint": "/products-join", "method": "GET"},
#     #         )

#     # @patch('..main.sentry_sdk')
#     # def test_success_endpoint(self, mock_sentry):
#     #     from ..main import app  # Import here to apply patched environment variables
#     #     with app.test_client() as client:
#     #         response = client.get('/success')
            
#     #         self.assertEqual(response.status_code, 200)
#     #         self.assertEqual(response.data.decode(), "success from flask")
#     #         mock_sentry.metrics.incr.assert_called_with(
#     #             key="endpoint_call",
#     #             value=1,
#     #             tags={"endpoint": "/success", "method": "GET"},
#     #         )

#     # @patch('..main.sentry_sdk.capture_exception')
#     # def test_handled_exception(self, mock_capture_exception):
#     #     from ..main import app  # Import here to apply patched environment variables
#     #     with app.test_client() as client:
#     #         response = client.get('/handled')
            
#     #         self.assertEqual(response.status_code, 200)
#     #         self.assertEqual(response.data.decode(), "failed")
#     #         mock_capture_exception.assert_called_once()

#     # @patch('..main.sentry_sdk.capture_exception')
#     # def test_unhandled_exception(self, mock_capture_exception):
#     #     from ..main import app  # Import here to apply patched environment variables
#     #     with app.test_client() as client:
#     #         with self.assertRaises(KeyError):
#     #             client.get('/unhandled')
#     #         mock_capture_exception.assert_called_once()

if __name__ == '__main__':
    unittest.main()
