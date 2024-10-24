import unittest

from hartsim.config import Configuration


class TestConfig(unittest.TestCase):

    def test_port_reading(self):
        expected = 'Qwerty123'
        data = { 'port': expected }
        target = Configuration.from_dict(data)
        self.assertEqual(target.port, expected)

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
