import unittest

from hartsim import U8


class TestPayloads(unittest.TestCase):

    def test_u8_default_value_is_zero(self):
        expected = 0
        target = U8()
        self.assertEqual(target.get_value(), expected)

    def test_u8_non_default_value(self):
        expected = value = 123
        target = U8(value)
        self.assertEqual(target.get_value(), expected)

    def test_u8_negative_value(self):
        value = -123
        expected = 123
        target = U8(value)
        self.assertEqual(target.get_value(), expected)

    def test_u8_wider_value(self):
        value = 257
        expected = 1
        target = U8(value)
        self.assertEqual(target.get_value(), expected)

    def test_u8_wider_negative_value(self):
        value = -257
        expected = 1
        target = U8(value)
        self.assertEqual(target.get_value(), expected)

    def test_u8_deserialize(self):
        serialized = bytearray([1, 2, 3, 4, 5])
        expected = 4
        target = U8()
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        next(serialized_iterator)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        self.assertEqual(target.get_value(), expected)

    def test_u8_serialize(self):
        value = 231
        expected = bytearray([value])
        expectedIndex = 0
        target = U8(value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex])
            expectedIndex += 1


if __name__ == '__main__':
    unittest.main()
