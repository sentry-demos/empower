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
class TestSpecials(unittest.TestCase):
    def setUp(self):
        # Sample test data
        self.test_products = [
            {
                "id": "1",
                "title": "Product 1",
                "description": "Description 1",
                "price": 10,
                "reviews": [{"rating": 5}]
            },
            {
                "id": "2",
                "title": "Product 2",
                "description": "Description 2",
                "price": 20,
                "reviews": [{"rating": 4}]
            },
            {
                "id": "3",
                "title": "Product 3",
                "description": "Description 3",
                "price": 30,
                "reviews": [{"rating": 3}]
            }
        ]

    @patch('requests.get')  # Mock the Ruby backend API call
    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_success(self, mock_sentry, mock_get_products_join, mock_requests_get):
        # Setup mocks
        mock_get_products_join.return_value = json.dumps(self.test_products)
        mock_requests_get.return_value.raise_for_status = MagicMock()
        
        # Import app here to apply patched environment variables
        from src.main import app
        
        with app.test_client() as client:
            # Make request to endpoint
            response = client.get('/get_specials')
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            
            # Parse response data
            data = json.loads(response.data)
            
            # Verify only first 2 products are returned
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['id'], "1")
            self.assertEqual(data[1]['id'], "2")
            
            # Verify Sentry metrics were called
            mock_sentry.metrics.incr.assert_called_with(
                key="endpoint_call",
                value=1,
                tags={"endpoint": "/get_specials", "method": "GET"},
            )
            
            # Verify Ruby backend API was called
            mock_requests_get.assert_called_once()

    @patch('requests.get')
    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_empty_products(self, mock_sentry, mock_get_products_join, mock_requests_get):
        # Setup mocks with empty product list
        mock_get_products_join.return_value = json.dumps([])
        mock_requests_get.return_value.raise_for_status = MagicMock()
        
        from src.main import app
        
        with app.test_client() as client:
            response = client.get('/get_specials')
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            
            # Verify empty array is returned
            data = json.loads(response.data)
            self.assertEqual(len(data), 0)

    @patch('requests.get')
    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_db_error(self, mock_sentry, mock_get_products_join, mock_requests_get):
        # Setup mock to raise exception
        mock_get_products_join.side_effect = Exception("Database error")
        
        from src.main import app
        
        with app.test_client() as client:
            with self.assertRaises(Exception) as context:
                client.get('/get_specials')
            
            # Verify error was captured by Sentry
            mock_sentry.capture_exception.assert_called_once()
            self.assertTrue("Database error" in str(context.exception))

    @patch('requests.get')
    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_ruby_api_error(self, mock_sentry, mock_get_products_join, mock_requests_get):
        # Setup mocks
        mock_get_products_join.return_value = json.dumps(self.test_products)
        mock_requests_get.side_effect = Exception("Ruby API error")
        
        from src.main import app
        
        with app.test_client() as client:
            response = client.get('/get_specials')
            
            # Verify response still succeeds even if Ruby API fails
            self.assertEqual(response.status_code, 200)
            
            # Verify error was captured by Sentry
            mock_sentry.capture_exception.assert_called_once()
            
            # Verify products were still returned
            data = json.loads(response.data)
            self.assertEqual(len(data), 2)

if __name__ == '__main__':
    unittest.main() 