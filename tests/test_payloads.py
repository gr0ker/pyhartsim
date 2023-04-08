import unittest

from hartsim import Unsigned, U8, U16, U24, U32


class TestPayloads(unittest.TestCase):

    def test_unsigned_default_value_is_zero(self):
        expected = 0
        target = Unsigned()
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_default_size_is_one(self):
        expected = 1
        target = Unsigned()
        self.assertEqual(target.get_size(), expected)

    def test_unsigned_min_size_is_one(self):
        size = 0
        expected = 1
        target = Unsigned(size=size)
        self.assertEqual(target.get_size(), expected)

    def test_unsigned_max_size_is_four(self):
        size = 5
        expected = 4
        target = Unsigned(size=size)
        self.assertEqual(target.get_size(), expected)

    def test_unsigned_non_default_value_1_byte(self):
        expected = value = 123
        target = Unsigned(value)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_non_default_value_2_bytes(self):
        size = 2
        expected = value = 256
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_non_default_value_3_bytes(self):
        size = 3
        expected = value = 65536
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_non_default_value_4_bytes(self):
        size = 4
        expected = value = 16777216
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_max_value_4_bytes(self):
        size = 4
        expected = value = 4294967295
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_negative_value_1_byte(self):
        value = -123
        expected = 123
        target = Unsigned(value)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_negative_value_2_bytes(self):
        size = 2
        value = -256
        expected = 256
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_negative_value_3_bytes(self):
        size = 3
        value = -65536
        expected = 65536
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_negative_value_4_bytes(self):
        size = 4
        value = -16777216
        expected = 16777216
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_max_negative_value_4_bytes(self):
        size = 4
        value = -4294967295
        expected = 4294967295
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_wider_value_1_byte(self):
        value = 257
        expected = 1
        target = Unsigned(value)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_wider_value_2_bytes(self):
        size = 2
        value = 65537
        expected = 1
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_wider_value_3_bytes(self):
        size = 3
        value = 16777217
        expected = 1
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_wider_value_4_bytes(self):
        size = 4
        value = 4294967297
        expected = 1
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_wider_negative_value_1_byte(self):
        value = -257
        expected = 1
        target = Unsigned(value)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_wider_negative_value_2_bytes(self):
        size = 2
        value = -65537
        expected = 1
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_wider_negative_value_3_bytes(self):
        size = 3
        value = -16777217
        expected = 1
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_wider_negative_value_4_bytes(self):
        size = 4
        value = -4294967297
        expected = 1
        target = Unsigned(value, size)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_deserialize_1_byte(self):
        serialized = bytearray([0x01, 0x02, 0x03, 0x04, 0x05])
        expected = 0x02
        target = Unsigned()
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_deserialize_2_bytes(self):
        size = 2
        serialized = bytearray([0x01, 0x02, 0x03, 0x04, 0x05])
        expected = 0x0203
        target = Unsigned(size=size)
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_deserialize_3_bytes(self):
        size = 3
        serialized = bytearray([0x01, 0x02, 0x03, 0x04, 0x05])
        expected = 0x020304
        target = Unsigned(size=size)
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_deserialize_4_bytes(self):
        size = 4
        serialized = bytearray([0x01, 0x02, 0x03, 0x04, 0x05])
        expected = 0x02030405
        target = Unsigned(size=size)
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        self.assertEqual(target.get_value(), expected)

    def test_unsigned_serialize_1_byte(self):
        size = 1
        value = 0x05
        expected = bytearray([0x05])
        expectedIndex = 0
        target = Unsigned(value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, size)

    def test_unsigned_serialize_2_bytes(self):
        size = 2
        value = 0x0504
        expected = bytearray([0x05, 0x04])
        expectedIndex = 0
        target = Unsigned(value, size)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, size)

    def test_unsigned_serialize_3_bytes(self):
        size = 3
        value = 0x050403
        expected = bytearray([0x05, 0x04, 0x03])
        expectedIndex = 0
        target = Unsigned(value, size)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, size)

    def test_unsigned_serialize_4_bytes(self):
        size = 4
        value = 0x05040302
        expected = bytearray([0x05, 0x04, 0x03, 0x02])
        expectedIndex = 0
        target = Unsigned(value, size)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, size)

    def test_u8_size_is_one(self):
        expected = 1
        target = U8()
        self.assertEqual(target.get_size(), expected)

    def test_u16_size_is_two(self):
        expected = 2
        target = U16()
        self.assertEqual(target.get_size(), expected)

    def test_u24_size_is_three(self):
        expected = 3
        target = U24()
        self.assertEqual(target.get_size(), expected)

    def test_u32_size_is_four(self):
        expected = 4
        target = U32()
        self.assertEqual(target.get_size(), expected)


if __name__ == '__main__':
    unittest.main()
