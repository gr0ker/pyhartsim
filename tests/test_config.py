import unittest

from hartsim.config import Configuration
from unittest.mock import patch, mock_open


class TestConfig(unittest.TestCase):

    def test_port_reading(self):
        expected = 'Qwerty123'
        data = { 'port': expected }
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                target = Configuration.load('some-path')
                self.assertEqual(target.port, expected)

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
