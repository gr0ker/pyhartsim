import math
import unittest

from attr import dataclass
import pytest

from hartsim import Unsigned, U8, U16, U24, U32, PayloadSequence
from hartsim.payloads import GreedyU8Array, Payload, F32, Ascii, PackedAscii


@dataclass
class PayloadSequenceExample(PayloadSequence):
    first_byte: U8 = U8()
    second_byte: U8 = U8()
    third_word: U16 = U16()


@dataclass
class PayloadSequenceOptionalExample(PayloadSequence):
    first_byte: U8 = U8()
    second_byte: U8 = U8()
    third_word: U16 = U16(is_optional=True)


@dataclass
class PayloadSequenceMiddleOptionalExample(PayloadSequence):
    first_byte: U8 = U8()
    second_byte: U8 = U8(is_optional=True)
    third_word: U16 = U16()


class TestPayloads(unittest.TestCase):

    def test_abstract_serialize_does_nothing(self):
        target = Payload()
        iterator = iter(target)
        noItems = False
        try:
            next(iterator)
        except StopIteration:
            noItems = True
        self.assertTrue(noItems)

    def test_abstract_deserialize_does_not_throw(self):
        serialized = bytearray([0x01, 0x02, 0x03, 0x04, 0x05])
        target = Payload()
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)

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

    def test_float_default_value_is_nan(self):
        target = F32()
        self.assertTrue(math.isnan(target.get_value()))

    def test_float_default_size_is_four(self):
        expected = 4
        target = F32()
        self.assertEqual(target.get_size(), expected)

    def test_float_deserialize(self):
        serialized = bytearray([0x01, 0x3f, 0x9e, 0x06, 0x4b])
        expected = 1.2345670461654663
        target = F32()
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        actual_value = target.get_value()
        self.assertEqual(actual_value, expected)
        self.assertEqual(type(actual_value), float)

    def test_float_serialize(self):
        size = 4
        value = 1.234567
        expected = bytearray([0x3f, 0x9e, 0x06, 0x4b])
        expectedIndex = 0
        target = F32(value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, size)

    def test_ascii_default_value_is_empty(self):
        expected = ""
        target = Ascii(32)
        self.assertEqual(target.get_value(), expected)

    def test_ascii_min_size_is_one(self):
        size = 0
        expected = 1
        target = Ascii(size)
        self.assertEqual(target.get_size(), expected)

    def test_ascii_cut_to_size(self):
        size = 4
        value = "This is a test"
        expected = "This"
        target = Ascii(size)
        target.set_value(value)
        self.assertEqual(target.get_value(), expected)

    def test_ascii_deserialize(self):
        size = 32
        serialized = bytearray([0x20,
                                0x54, 0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20,
                                0x61, 0x20, 0x74, 0x65, 0x73, 0x74, 0x2e, 0x20,
                                0x44, 0x6f, 0x65, 0x73, 0x20, 0x69, 0x74, 0x20,
                                0x70, 0x61, 0x73, 0x73, 0x3f, 0x20, 0x48, 0x6d])
        expected = "This is a test. Does it pass? Hm"
        target = Ascii(size)
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        self.assertEqual(target.get_value(), expected)

    def test_ascii_serialize(self):
        size = 32
        value = "This is a test. Does it pass? Hm"
        expected = bytearray([0x54, 0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20,
                              0x61, 0x20, 0x74, 0x65, 0x73, 0x74, 0x2e, 0x20,
                              0x44, 0x6f, 0x65, 0x73, 0x20, 0x69, 0x74, 0x20,
                              0x70, 0x61, 0x73, 0x73, 0x3f, 0x20, 0x48, 0x6d])
        expectedIndex = 0
        target = Ascii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, size)

    def test_ascii_serialize_pad_spaces(self):
        size = 32
        value = "This is a test."
        expected = bytearray([0x54, 0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20,
                              0x61, 0x20, 0x74, 0x65, 0x73, 0x74, 0x2e, 0x20,
                              0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20,
                              0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20])
        expectedIndex = 0
        target = Ascii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, size)

    def test_packed_ascii_value_handling(self):
        size = 32
        value = "`This~is a {test}.`"
        expected = "?THIS?IS A ?TEST?.?"
        target = PackedAscii(size, value)
        self.assertEqual(target.get_value(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_wider_value(self):
        size = 14
        value = "THIS IS A WIDEST"
        expected = "THIS IS A WIDE"
        target = PackedAscii(size, value)
        self.assertEqual(target.get_value(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_packed_size_1(self):
        size = 1
        expected = 1
        target = PackedAscii(size)
        self.assertEqual(target.get_packed_size(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_size_2(self):
        size = 2
        expected = 2
        target = PackedAscii(size)
        self.assertEqual(target.get_packed_size(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_size_3(self):
        size = 3
        expected = 3
        target = PackedAscii(size)
        self.assertEqual(target.get_packed_size(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_size_4(self):
        size = 4
        expected = 3
        target = PackedAscii(size)
        self.assertEqual(target.get_packed_size(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_packed_size_5(self):
        size = 5
        expected = 4
        target = PackedAscii(size)
        self.assertEqual(target.get_packed_size(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_size_6(self):
        size = 6
        expected = 5
        target = PackedAscii(size)
        self.assertEqual(target.get_packed_size(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_size_7(self):
        size = 7
        expected = 6
        target = PackedAscii(size)
        self.assertEqual(target.get_packed_size(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_size_8(self):
        size = 8
        expected = 6
        target = PackedAscii(size)
        self.assertEqual(target.get_packed_size(), expected)
        self.assertEqual(target.get_size(), size)

    def test_packed_ascii_serialize_1(self):
        size = 1
        value = "1"
        expected = bytearray([0xC4])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_2(self):
        size = 2
        value = "12"
        expected = bytearray([0xC7, 0x20])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_3(self):
        size = 3
        value = "123"
        expected = bytearray([0xC7, 0x2C, 0xC0])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_4(self):
        size = 4
        value = "1234"
        expected = bytearray([0xC7, 0x2C, 0xF4])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_5(self):
        size = 5
        value = "12345"
        expected = bytearray([0xC7, 0x2C, 0xF4, 0xD4])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_6(self):
        size = 6
        value = "123456"
        expected = bytearray([0xC7, 0x2C, 0xF4, 0xD7, 0x60])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_7(self):
        size = 7
        value = "1234567"
        expected = bytearray([0xC7, 0x2C, 0xF4, 0xD7, 0x6D, 0xC0])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_8(self):
        size = 8
        value = "12345678"
        expected = bytearray([0xC7, 0x2C, 0xF4, 0xD7, 0x6D, 0xF8])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_8_1(self):
        size = 8
        value = "1"
        expected = bytearray([0xC6, 0x08, 0x20, 0x82, 0x08, 0x20])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_8_2(self):
        size = 8
        value = "12"
        expected = bytearray([0xC7, 0x28, 0x20, 0x82, 0x08, 0x20])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_8_3(self):
        size = 8
        value = "123"
        expected = bytearray([0xC7, 0x2C, 0xE0, 0x82, 0x08, 0x20])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_packed_ascii_serialize_8_4(self):
        size = 8
        value = "1234"
        expected = bytearray([0xC7, 0x2C, 0xF4, 0x82, 0x08, 0x20])
        expectedIndex = 0
        target = PackedAscii(size, value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_ascii_deserialize_digits(self):
        size = 8
        serialized = bytearray([0x01, 0xC7, 0x2C, 0xF4, 0xD7, 0x6D, 0xF8])
        expected = "12345678"
        target = PackedAscii(size)
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        self.assertEqual(target.get_value(), expected)

    def test_ascii_deserialize_alpha(self):
        size = 8
        serialized = bytearray(
            [0x00, 0x05, 0x30, 0xC9, 0x26, 0xDD, 0xA0, 0x00])
        expected = "ASCII-6 "
        target = PackedAscii(size)
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        self.assertEqual(target.get_value(), expected)

    def test_greedy_u8_array_default_value_is_empty(self):
        expected = bytearray(b'')
        target = GreedyU8Array()
        self.assertEqual(target.get_value(), expected)

    def test_greedy_u8_array_min_size_is_zero(self):
        expected = 0
        target = GreedyU8Array()
        self.assertEqual(target.get_size(), expected)

    def test_greedy_u8_array_init_value(self):
        value = bytearray([0x01, 0x02, 0x03, 0x04, 0x05])
        expected = value
        target = GreedyU8Array(value)
        self.assertEqual(target.get_value(), expected)

    def test_greedy_u8_array_assign_value(self):
        value = bytearray([0x06, 0x07, 0x08])
        expected = value
        target = GreedyU8Array()
        target.set_value(value)
        self.assertEqual(target.get_value(), expected)

    def test_greedy_u8_array_deserialize(self):
        serialized = bytearray([0x20,
                                0x54, 0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20,
                                0x61, 0x20, 0x74, 0x65, 0x73, 0x74, 0x2e, 0x20,
                                0x44, 0x6f, 0x65, 0x73, 0x20, 0x69, 0x74, 0x20,
                                0x70, 0x61, 0x73, 0x73, 0x3f, 0x20, 0x48, 0x6d])
        expected = serialized
        target = GreedyU8Array()
        serialized_iterator = iter(serialized)
        next(serialized_iterator)
        target.deserialize(serialized_iterator)
        self.assertEqual(target.get_value(), expected[1:])

    def test_greedy_u8_array_serialize(self):
        expected = bytearray([0x54, 0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20,
                              0x61, 0x20, 0x74, 0x65, 0x73, 0x74, 0x2e, 0x20,
                              0x44, 0x6f, 0x65, 0x73, 0x20, 0x69, 0x74, 0x20,
                              0x70, 0x61, 0x73, 0x73, 0x3f, 0x20, 0x48, 0x6d])
        value = expected
        expectedIndex = 0
        target = GreedyU8Array(value)
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_payload_sequence_is_serialized(self):
        expected = bytearray([0x04, 0x03, 0x02, 0x01])
        target = PayloadSequenceExample()
        target.first_byte.set_value(0x04)
        target.second_byte.set_value(0x03)
        target.third_word.set_value(0x0201)
        expectedIndex = 0
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))

    def test_payload_sequence_is_deserialized(self):
        serialized = bytearray([0x09, 0x08, 0x07, 0x06])
        target = PayloadSequenceExample()
        target.deserialize(iter(serialized))
        self.assertEqual(target.first_byte.get_value(), 0x09)
        self.assertEqual(target.second_byte.get_value(), 0x08)
        self.assertEqual(target.third_word.get_value(), 0x0706)

    def test_payload_sequence_raises_when_not_enough_bytes(self):
        with pytest.raises(StopIteration):
            serialized = bytearray([0x09, 0x08])
            target = PayloadSequenceExample()
            target.deserialize(iter(serialized))

    def test_payload_sequence_skips_optional(self):
        serialized = bytearray([0x09, 0x08])
        target = PayloadSequenceOptionalExample()
        target.deserialize(iter(serialized))
        self.assertEqual(target.first_byte.get_value(), 0x09)
        self.assertEqual(target.second_byte.get_value(), 0x08)
        self.assertTrue(target.third_word.is_skipped())

    def test_payload_sequence_is_serialized_without_skipped(self):
        expected = bytearray([0x04, 0x02, 0x01])
        target = PayloadSequenceMiddleOptionalExample()
        target.first_byte.set_value(0x04)
        target.second_byte.set_value(0x03)
        target.second_byte.skip()
        target.third_word.set_value(0x0201)
        expectedIndex = 0
        for item in target:
            self.assertEqual(item, expected[expectedIndex], f"{expectedIndex}")
            expectedIndex += 1
        self.assertEqual(expectedIndex, len(expected))


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
