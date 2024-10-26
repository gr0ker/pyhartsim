import unittest

from hartsim import HartFrame, FrameType
from hartsim.framingutils import HartFrameBuilder


class TestFramingUtils(unittest.TestCase):

    def test_hart_frame_short_address_to_bytes(self):
        expected = bytearray([0x06, 0xaa, 0x00, 0x03, 0x01, 0x02, 0x03, 0xaf])
        target = HartFrame(FrameType.ACK, 0, short_address=42,
                           data=bytearray([0x01, 0x02, 0x03]))
        self.assertEqual(target.serialize(), expected)

    def test_hart_frame_short_address_burst_mode_to_bytes(self):
        expected = bytearray([0x06, 0xea, 0x00, 0x03, 0x01, 0x02, 0x03, 0xef])
        target = HartFrame(FrameType.ACK, 0, short_address=42, is_burst=True,
                           data=bytearray([0x01, 0x02, 0x03]))
        self.assertEqual(target.serialize(), expected)

    def test_hart_frame_long_address_to_bytes(self):
        expected = bytearray(
            [0x86, 0x92, 0x34, 0x56, 0x78, 0x9A, 0x00, 0x03, 0x01, 0x02, 0x03, 0x97])
        target = HartFrame(FrameType.ACK,
                           0,
                           is_long_address=True,
                           long_address=0x123456789A,
                           data=bytearray([0x01, 0x02, 0x03]))
        self.assertEqual(target.serialize(), expected)

    def test_hart_frame_long_address_burst_mode_to_bytes(self):
        expected = bytearray(
            [0x86, 0xD2, 0x34, 0x56, 0x78, 0x9A, 0x00, 0x03, 0x01, 0x02, 0x03, 0xD7])
        target = HartFrame(FrameType.ACK,
                           0,
                           is_long_address=True,
                           long_address=0x123456789A,
                           is_burst=True,
                           data=bytearray([0x01, 0x02, 0x03]))
        self.assertEqual(target.serialize(), expected)

    def test_hart_frame_short_address_deserialize(self):
        serialized = iter(
            bytearray([0xFF, 0x10, 0xFF, 0xFF, 0x06, 0xaa, 0x00, 0x03, 0x01, 0x02, 0x03,
                       0xaf]))
        builder = HartFrameBuilder()
        builder.collect(serialized)
        target = builder.dequeue()
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
            bytearray([0xFF, 0xFF, 0x10, 0xFF, 0xFF, 0x86, 0x92, 0x34, 0x56, 0x78,
                       0x9A, 0x00, 0x03, 0x01, 0x02, 0x03, 0x97]))
        builder = HartFrameBuilder()
        builder.collect(serialized)
        target = builder.dequeue()
        self.assertEqual(target.type, FrameType.ACK)
        self.assertEqual(target.is_long_address, True)
        self.assertEqual(target.long_address, 0x123456789A)
        self.assertEqual(target.is_primary_master, True)
        self.assertEqual(target.is_burst, False)
        self.assertEqual(target.command_number, 0)
        self.assertEqual(target.data, bytearray([0x01, 0x02, 0x03]))
        self.assertEqual(target.check_sum, 0x97)

    def test_hart_frame_long_address_no_data_deserialize(self):
        serialized = iter(
            bytearray([0xFF, 0xFF, 0x86, 0x92, 0x34, 0x56, 0x78,
                       0x9A, 0x00, 0x00, 0x97]))
        builder = HartFrameBuilder()
        builder.collect(serialized)
        target = builder.dequeue()
        self.assertEqual(target.type, FrameType.ACK)
        self.assertEqual(target.is_long_address, True)
        self.assertEqual(target.long_address, 0x123456789A)
        self.assertEqual(target.is_primary_master, True)
        self.assertEqual(target.is_burst, False)
        self.assertEqual(target.command_number, 0)
        self.assertEqual(target.data, bytearray([]))
        self.assertEqual(target.check_sum, 0x97)

    def test_hart_frame_default_constructor_format(self):
        expected = 'TYP(BACK) MST(PRI) MOD(POL) ADR(0) CMD(00123) SUM(???) DAT(NONE)'
        target = HartFrame(FrameType.BACK, 123)
        self.assertEqual(f'{target}', expected)

    def test_hart_frame_default_no_short_address_format(self):
        expected = 'TYP(BACK) MST(PRI) MOD(POL) ADR(???) CMD(00123) SUM(???) DAT(NONE)'
        # noinspection PyTypeChecker
        target = HartFrame(FrameType.BACK, 123, short_address=None)
        self.assertEqual(f'{target}', expected)

    def test_hart_frame_default_no_long_address_format(self):
        expected = 'TYP(BACK) MST(PRI) MOD(POL) ADR(???) CMD(00123) SUM(???) DAT(NONE)'
        # noinspection PyTypeChecker
        target = HartFrame(FrameType.BACK, 123,
                           is_long_address=True, long_address=None)
        self.assertEqual(f'{target}', expected)

    def test_hart_frame_default_invalid_checksum_format(self):
        expected = 'TYP(BACK) MST(PRI) MOD(POL) ADR(0) CMD(00123) SUM(0x00!) DAT(NONE)'
        target = HartFrame(FrameType.BACK, 123, check_sum=0)
        self.assertEqual(f'{target}', expected)

    def test_hart_frame_default_valid_checksum_format(self):
        expected = 'TYP(BACK) MST(PRI) MOD(POL) ADR(0) CMD(00123) SUM(0xFA ) DAT(NONE)'
        target = HartFrame(FrameType.BACK, 123, check_sum=0xFA)
        self.assertEqual(f'{target}', expected)

    def test_hart_frame_constructor_format(self):
        expected =\
            'TYP(STX) MST(SEC) MOD(BST) ADR(0x123456789A) CMD(00234) SUM(0x56!) \
DAT(0x010203)'
        target = HartFrame(FrameType.STX,
                           234,
                           is_long_address=True,
                           long_address=0x123456789A,
                           is_primary_master=False,
                           is_burst=True,
                           data=bytearray([0x01, 0x02, 0x03]),
                           check_sum=0x56)
        self.assertEqual(f'{target}', expected)

    def test_hart_frame_undefined_format(self):
        expected = 'TYP(???) MST(???) MOD(???) ADR(???) CMD(???) SUM(???) DAT(???)'
        # noinspection PyTypeChecker
        target = HartFrame(None, None, None, None,
                           None, None, None, None, None)
        self.assertEqual(f'{target}', expected)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
