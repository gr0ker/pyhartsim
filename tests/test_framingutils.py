import unittest

from hartsim import HartFrame, FrameType


class TestFramingUtils(unittest.TestCase):

    def test_hart_frame_short_address_to_bytes(self):
        expected = bytearray([0x06, 0xaa, 0x00, 0x03, 0x01, 0x02, 0x03, 0xaf])
        target = HartFrame(FrameType.ACK, 0, short_address=42,
                           data=bytearray([0x01, 0x02, 0x03]))
        self.assertEqual(target.to_bytes(), expected)

    def test_hart_frame_long_address_to_bytes(self):
        expected = bytearray(
            [0x86, 0x92, 0x34, 0x56, 0x78, 0x9A, 0x00, 0x03, 0x01, 0x02, 0x03, 0x97])
        target = HartFrame(FrameType.ACK,
                           0,
                           is_long_address=True,
                           long_address=bytearray(
                               [0x12, 0x34, 0x56, 0x78, 0x9A]),
                           data=bytearray([0x01, 0x02, 0x03]))
        self.assertEqual(target.to_bytes(), expected)

    def test_hart_frame_short_address_deserialize(self):
        serialized = iter(
            bytearray([0xFF, 0xFF, 0x06, 0xaa, 0x00, 0x03, 0x01, 0x02, 0x03, 0xaf]))
        target = HartFrame.deserialize(serialized)
        self.assertEqual(target.type, FrameType.ACK)
        self.assertEqual(target.is_long_address, False)
        self.assertEqual(target.short_address, 42)
        self.assertEqual(target.is_primary_master, True)
        self.assertEqual(target.is_burst, False)
        self.assertEqual(target.command_number, 0)
        self.assertEqual(target.data, bytearray([0x01, 0x02, 0x03]))
        self.assertEqual(target.check_sum, 0xAF)

    def test_hart_frame_long_address_deserialize(self):
        serialized = iter(
            bytearray([0xFF, 0xFF, 0x86, 0x92, 0x34, 0x56, 0x78,
                       0x9A, 0x00, 0x03, 0x01, 0x02, 0x03, 0x97]))
        target = HartFrame.deserialize(serialized)
        self.assertEqual(target.type, FrameType.ACK)
        self.assertEqual(target.is_long_address, True)
        self.assertEqual(target.long_address, bytearray(
            [0x12, 0x34, 0x56, 0x78, 0x9A]))
        self.assertEqual(target.is_primary_master, True)
        self.assertEqual(target.is_burst, False)
        self.assertEqual(target.command_number, 0)
        self.assertEqual(target.data, bytearray([0x01, 0x02, 0x03]))
        self.assertEqual(target.check_sum, 0x97)


if __name__ == '__main__':
    unittest.main()
