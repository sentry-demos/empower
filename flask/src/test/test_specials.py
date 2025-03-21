import unittest
from unittest.mock import patch, MagicMock
from flask import json

@patch.dict('os.environ', {
    'RELEASE': 'test-release',
    'FLASK_APP_DSN': 'https://xxxxyyyyy@o11111.sentry.io/11111',
    'FLASK_ENV': 'test',
    'RUBY_BACKEND': 'http://test-backend',
    'RUN_SLOW_PROFILE': 'false',
    'DB_HOST': 'test-host',
    'DB_DATABASE': 'test-db',
    'DB_USERNAME': 'test-user',
    'DB_PASSWORD': 'test-password'
})
@patch('src.db.create_engine')
class TestSpecials(unittest.TestCase):
    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_success(self, mock_sentry, mock_get_products_join, mock_create_engine):
        # Mock data with more than 2 products to verify slicing
        mock_data = [
            {"id": 1, "title": "Product 1", "reviews": []},
            {"id": 2, "title": "Product 2", "reviews": []},
            {"id": 3, "title": "Product 3", "reviews": []},
            {"id": 4, "title": "Product 4", "reviews": []}
        ]
        mock_get_products_join.return_value = json.dumps(mock_data)
        
        from src.main import app  # Import here to apply patched environment variables
        with app.test_client() as client:
            response = client.get('/get_specials')
            
            # Verify response status code
            self.assertEqual(response.status_code, 200)
            
            # Verify response data
            response_data = json.loads(response.data)
            self.assertEqual(len(response_data), 2)  # Should only return 2 products
            self.assertEqual(response_data[0]['id'], 1)  # First product
            self.assertEqual(response_data[1]['id'], 2)  # Second product
            
            # Verify Sentry metrics were called
            mock_sentry.metrics.incr.assert_called_with(
                key="endpoint_call",
                value=1,
                tags={"endpoint": "/get_specials", "method": "GET"},
            )

    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_single_product(self, mock_sentry, mock_get_products_join, mock_create_engine):
        # Mock data with only one product
        mock_data = [{"id": 1, "title": "Product 1", "reviews": []}]
        mock_get_products_join.return_value = json.dumps(mock_data)
        
        from src.main import app
        with app.test_client() as client:
            response = client.get('/get_specials')
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(len(response_data), 1)  # Should return the one product
            self.assertEqual(response_data[0]['id'], 1)

    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_no_products(self, mock_sentry, mock_get_products_join, mock_create_engine):
        # Mock empty product list
        mock_get_products_join.return_value = json.dumps([])
        
        from src.main import app
        with app.test_client() as client:
            response = client.get('/get_specials')
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(len(response_data), 0)  # Should return empty list

    @patch('src.main.get_products_join')
    @patch('src.main.sentry_sdk')
    def test_get_specials_error_handling(self, mock_sentry, mock_get_products_join, mock_create_engine):
        # Mock an error in get_products_join
        mock_get_products_join.side_effect = Exception("Database error")
        
        from src.main import app
        with app.test_client() as client:
            # Should raise the exception
            with self.assertRaises(Exception) as context:
                client.get('/get_specials')
            
            self.assertEqual(str(context.exception), "Database error")
            # Verify Sentry exception was captured
            mock_sentry.capture_exception.assert_called_once()

if __name__ == '__main__':
    unittest.main() 