from enum import Enum
from functools import reduce
from typing import Iterator

State = Enum('State', [
    'UNKNOWN',
    'PREAMBLES',
    'SHORT_ADDRESS',
    'LONG_ADDRESS',
    'COMMAND_NUMBER',
    'BYTE_COUNT',
    'DATA',
    'CHECK_SUM',
    'COMPLETE'])


class FrameType(Enum):
    BACK = 1
    STX = 2
    ACK = 6

    def __str__(self):
        return self.name

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


DELIMITER_MASK = 0x17
LONG_ADDRESS_MASK = 0x80
PRIMARY_MASTER_MASK = 0x80
BURST_MODE_MASK = 0x40
ADDRESS_MASK = 0x3F


class HartFrame:
    @classmethod
    def deserialize(self, iterator: Iterator[int]):
        state = State.UNKNOWN
        type = None
        command_number = None
        is_long_address = None
        short_address = None
        long_address = None
        is_primary_master = None
        is_burst = None
        payload = None
        check_sum = None
        number_of_preambles = 0
        for item in iterator:
            match state:
                case State.UNKNOWN:
                    if item == 0xFF:
                        number_of_preambles += 1
                    else:
                        number_of_preambles = 0

                    if number_of_preambles >= 2:
                        state = State.PREAMBLES
                case State.PREAMBLES:
                    if item != 0xFF:
                        maskedItem = item & DELIMITER_MASK
                        if FrameType.has_value(maskedItem):
                            type = FrameType(maskedItem)
                            is_long_address = (
                                item & LONG_ADDRESS_MASK) == LONG_ADDRESS_MASK
                            if is_long_address:
                                state = State.LONG_ADDRESS
                            else:
                                state = State.SHORT_ADDRESS
                            long_address = bytearray()
                            short_address = 0
                        else:
                            state = State.UNKNOWN
                case State.SHORT_ADDRESS:
                    short_address = item & ADDRESS_MASK
                    is_primary_master = (
                        item & PRIMARY_MASTER_MASK) == PRIMARY_MASTER_MASK
                    is_burst = (
                        item & BURST_MODE_MASK) == BURST_MODE_MASK
                    state = State.COMMAND_NUMBER
                case State.LONG_ADDRESS:
                    if len(long_address) == 0:
                        long_address.append(item & ADDRESS_MASK)
                        is_primary_master = (
                            item & PRIMARY_MASTER_MASK) == PRIMARY_MASTER_MASK
                        is_burst = (
                            item & BURST_MODE_MASK) == BURST_MODE_MASK
                    else:
                        long_address.append(item)
                    if len(long_address) == 5:
                        state = State.COMMAND_NUMBER
                case State.COMMAND_NUMBER:
                    command_number = item
                    state = State.BYTE_COUNT
                case State.BYTE_COUNT:
                    byte_count = item
                    if byte_count > 0:
                        state = State.DATA
                    else:
                        state = State.CHECK_SUM
                    payload = bytearray()
                case State.DATA:
                    payload.append(item)
                    if len(payload) == byte_count:
                        state = State.CHECK_SUM
                case State.CHECK_SUM:
                    check_sum = item
                    state = State.COMPLETE
                    break

        return HartFrame(type,
                         command_number,
                         is_long_address,
                         short_address,
                         long_address,
                         is_primary_master,
                         is_burst,
                         payload,
                         check_sum,
                         state)

    def __init__(self,
                 type: FrameType,
                 command_number: int,
                 is_long_address: bool = False,
                 short_address: int = 0,
                 long_address: bytearray = bytearray(),
                 is_primary_master: bool = True,
                 is_burst: bool = False,
                 data: bytearray = bytearray(),
                 check_sum: int = 0x00,
                 state: State = State.COMPLETE):
        self.type = type
        self.command_number = command_number
        self.is_long_address = is_long_address
        self.short_address = short_address
        self.long_address = long_address
        self.is_primary_master = is_primary_master
        self.is_burst = is_burst
        self.data = data
        self.check_sum = check_sum
        self.state = state

    def to_bytes(self):
        encoded = bytearray()

        # delimiter
        encoded.append(
            self.type.value | LONG_ADDRESS_MASK if self.is_long_address else self.type.value)

        # address
        if self.is_long_address:
            first_byte = self.long_address[0]
            if self.is_primary_master:
                first_byte |= PRIMARY_MASTER_MASK
            if self.is_burst:
                first_byte |= BURST_MODE_MASK
            encoded.append(first_byte)
            encoded.extend(self.long_address[1:])
        else:
            first_byte = self.short_address
            if self.is_primary_master:
                first_byte |= PRIMARY_MASTER_MASK
            if self.is_burst:
                first_byte |= BURST_MODE_MASK
            encoded.append(first_byte)

        # command number
        encoded.append(self.command_number)

        # byte count
        encoded.append(len(self.data))

        # data
        encoded.extend(self.data)

        # check byte
        self.check_sum = reduce(lambda x, y: x ^ y, encoded)
        encoded.append(self.check_sum)

        return encoded

    def __repr__(self):
        return f'{self.type} \
{"PRI" if self.is_primary_master else "SEC"}\
{" BST" if self.is_burst else ""} \
ADR({"".join("{:02X}".format(x) for x in self.long_address) if self.is_long_address else self.short_address}) \
CMD({self.command_number:03}) \
DAT({"".join("{:02X}".format(x) for x in self.data) if len(self.data) else "NO"}) \
SUM({self.check_sum:02X})'