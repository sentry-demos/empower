import unittest
from unittest.mock import patch, MagicMock
from flask.src import db

class TestDb(unittest.TestCase):

    @patch('flask.src.db.db.connect')
    def test_get_products(self, mock_connect):
        # Setup mock connection
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Mock the execute and fetchall functions
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = [{'id': 1, 'name': 'Product 1'}]
        mock_connection.execute = MagicMock(return_value=mock_execute)

        # Call the function under test
        result = db.get_products()

        # Assert that the result is as expected
        self.assertIn('Product 1', result)

    @patch('flask.src.db.db.connect')
    def test_get_inventory(self, mock_connect):
        # Setup mock
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = [{'productId': '1', 'quantity': 10}]
        mock_connection.execute = MagicMock(return_value=mock_execute)

        cart = {'quantities': {'1': 2}}
        result = db.get_inventory(cart)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['quantity'], 10)

# Add more tests for other functions like get_products_join() as needed

if __name__ == '__main__':
    unittest.main()
