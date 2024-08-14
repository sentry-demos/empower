import unittest
from unittest.mock import patch, MagicMock
from .utils import weighter, parseHeaders, get_iterator, yuval, chris
from datetime import datetime
from pytz import timezone

class TestUtils(unittest.TestCase):

    @patch('utils.datetime')
    def test_weighter_favors_faster_times(self, mock_datetime):
        # Mock datetime to return 12 PM
        mock_datetime.now.return_value = datetime(2024, 8, 13, 12, 0, 0, tzinfo=timezone('America/Los_Angeles'))

        def condition(current_hour, hour):
            return current_hour >= hour

        result = weighter(condition, 12)
        self.assertIn(result, [0.0125, 0.0625, 0.125, 0.1875, 0.25, 0.3125])

    @patch('utils.datetime')
    def test_weighter_favors_slower_times(self, mock_datetime):
        # Mock datetime to return 14 PM
        mock_datetime.now.return_value = datetime(2024, 8, 13, 14, 0, 0, tzinfo=timezone('America/Los_Angeles'))

        def condition(current_hour, hour):
            return current_hour <= hour

        result = weighter(condition, 12)
        self.assertIn(result, [0.0125, 0.0625, 0.125, 0.1875, 0.25, 0.3125])

    def test_parseHeaders(self):
        keys = ['Content-Type', 'Authorization', 'Custom-Header']
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token',
            'Custom-Header': 'custom_value',
            'Unused-Header': 'unused_value',
            'Invalid-Header': 'undefined'
        }

        expected_result = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token',
            'Custom-Header': 'custom_value',
        }

        result = parseHeaders(keys, headers)
        self.assertEqual(result, expected_result)

    def test_get_iterator(self):
        # Test some known Fibonacci sequence values
        self.assertEqual(get_iterator(0), 0)
        self.assertEqual(get_iterator(1), 1)
        self.assertEqual(get_iterator(2), 1)
        self.assertEqual(get_iterator(3), 2)
        self.assertEqual(get_iterator(4), 3)
        self.assertEqual(get_iterator(5), 5)
        self.assertEqual(get_iterator(6), 8)

    def test_get_iterator_negative_input(self):
        with self.assertLogs(level='INFO') as log:
            self.assertEqual(get_iterator(-1), None)
        self.assertIn("Incorrect input", log.output[0])

    def test_yuval(self):
        self.assertEqual(yuval("Any input"), "")

    def test_chris(self):
        self.assertEqual(chris(), "")

if __name__ == '__main__':
    unittest.main()
