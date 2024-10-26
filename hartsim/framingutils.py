from enum import Enum
from functools import reduce
from typing import Iterator

class State(Enum):
    UNKNOWN = 1
    PREAMBLES = 2
    SHORT_ADDRESS = 3
    LONG_ADDRESS = 4
    COMMAND_NUMBER = 5
    BYTE_COUNT = 6
    DATA = 7
    CHECK_SUM = 8

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
__UNDEFINED_NAME__ = '???'
__PRIMARY_NAME__ = 'PRI'
__SECONDARY_NAME__ = 'SEC'
__BURST_NAME__ = 'BST'
__POLLING_NAME__ = 'POL'
__NONE_NAME__ = 'NONE'


class HartFrame:
    def __init__(self,
                 type: FrameType,
                 command_number: int,
                 is_long_address: bool = False,
                 short_address: int = 0,
                 long_address: int = 0,
                 is_primary_master: bool = True,
                 is_burst: bool = False,
                 data: bytearray = bytearray(),
                 check_sum: int = None):
        self.type = type
        self.command_number = command_number
        self.is_long_address = is_long_address
        self.short_address = short_address
        self.long_address = long_address
        self.is_primary_master = is_primary_master
        self.is_burst = is_burst
        self.data = data
        self.check_sum = check_sum

    def serialize(self, update_check_sum: bool = True):
        encoded = bytearray()

        # delimiter
        try:
            encoded.append(
                self.type.value | LONG_ADDRESS_MASK
                if self.is_long_address
                else
                self.type.value)
        except AttributeError:
            encoded.append(0)

        # address
        if self.is_long_address:
            first_byte = self.long_address >> 32
            if self.is_primary_master:
                first_byte |= PRIMARY_MASTER_MASK
            if self.is_burst:
                first_byte |= BURST_MODE_MASK
            encoded.append(first_byte)
            encoded.append((self.long_address >> 24) & 0xFF)
            encoded.append((self.long_address >> 16) & 0xFF)
            encoded.append((self.long_address >> 8) & 0xFF)
            encoded.append(self.long_address & 0xFF)
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
        check_sum = reduce(lambda x, y: x ^ y, encoded)

        if update_check_sum:
            self.check_sum = check_sum

        encoded.append(check_sum)

        return encoded

    def is_valid(self) -> bool:
        return self.serialize(False)[-1] == self.check_sum

    def __repr__(self):
        if type(self.type) is FrameType and FrameType.has_value(self.type.value):
            kind = f'{self.type}'
        else:
            kind = __UNDEFINED_NAME__

        if type(self.is_primary_master) is bool:
            if self.is_primary_master:
                master = __PRIMARY_NAME__
            else:
                master = __SECONDARY_NAME__
        else:
            master = __UNDEFINED_NAME__

        if type(self.is_burst) is bool:
            if self.is_burst:
                burst = __BURST_NAME__
            else:
                burst = __POLLING_NAME__
        else:
            burst = __UNDEFINED_NAME__

        if type(self.is_long_address) is bool:
            if self.is_long_address:
                if type(self.long_address) is int:
                    address = '0x' + '{:010X}'.format(self.long_address)
                else:
                    address = __UNDEFINED_NAME__
            else:
                if type(self.short_address) is int:
                    address = self.short_address
                else:
                    address = __UNDEFINED_NAME__
        else:
            address = __UNDEFINED_NAME__

        try:
            command_number = f'{self.command_number:05}'
        except TypeError:
            command_number = __UNDEFINED_NAME__

        try:
            if self.is_valid():
                check_sum = f'0x{self.check_sum:02X} '
            else:
                check_sum = f'0x{self.check_sum:02X}!'
        except TypeError:
            check_sum = __UNDEFINED_NAME__

        try:
            if len(self.data) > 0:
                data = '0x' + ''.join('{:02X}'.format(x) for x in self.data)
            else:
                data = __NONE_NAME__
        except TypeError:
            data = __UNDEFINED_NAME__

        return f'\
TYP({kind}) \
MST({master}) \
MOD({burst}) \
ADR({address}) \
CMD({command_number}) \
SUM({check_sum}) \
DAT({data})'


class HartFrameBuilder:
    def __init__(self):
        self.__queue = []
        self.__reset__()

    def __reset__(self):
        self.state = State.UNKNOWN
        self.type = None
        self.command_number = None
        self.is_long_address = None
        self.short_address = None
        self.long_address = None
        self.is_primary_master = None
        self.is_burst = None
        self.payload = None
        self.check_sum = None
        self.number_of_preambles = 0
        self.long_address_length = 0

    def collect(self, iterator: Iterator[int]) -> bool:
        isNewFrameAvailable = False

        for item in iterator:
            if self.state == State.UNKNOWN:
                if item == 0xFF:
                    self.number_of_preambles += 1
                else:
                    self.number_of_preambles = 0

                if self.number_of_preambles >= 2:
                    self.state = State.PREAMBLES
            elif self.state == State.PREAMBLES:
                if item != 0xFF:
                    maskedItem = item & DELIMITER_MASK
                    if FrameType.has_value(maskedItem):
                        self.type = FrameType(maskedItem)
                        self.is_long_address = (
                            item & LONG_ADDRESS_MASK) == LONG_ADDRESS_MASK
                        if self.is_long_address:
                            self.state = State.LONG_ADDRESS
                        else:
                            self.state = State.SHORT_ADDRESS
                        self.long_address = 0
                        self.short_address = 0
                        self.long_address_length = 0
                    else:
                        self.state = State.UNKNOWN
            elif self.state == State.SHORT_ADDRESS:
                self.short_address = item & ADDRESS_MASK
                self.is_primary_master = (
                    item & PRIMARY_MASTER_MASK) == PRIMARY_MASTER_MASK
                self.is_burst = (
                    item & BURST_MODE_MASK) == BURST_MODE_MASK
                self.state = State.COMMAND_NUMBER
            elif self.state == State.LONG_ADDRESS:
                if self.long_address_length == 0:
                    self.long_address = (self.long_address << 8) | (
                        item & ADDRESS_MASK)
                    self.long_address_length += 1
                    self.is_primary_master = (
                        item & PRIMARY_MASTER_MASK) == PRIMARY_MASTER_MASK
                    self.is_burst = (
                        item & BURST_MODE_MASK) == BURST_MODE_MASK
                else:
                    self.long_address = (self.long_address << 8) | item
                    self.long_address_length += 1
                if self.long_address_length == 5:
                    self.state = State.COMMAND_NUMBER
            elif self.state == State.COMMAND_NUMBER:
                self.command_number = item
                self.state = State.BYTE_COUNT
            elif self.state == State.BYTE_COUNT:
                self.byte_count = item
                if self.byte_count > 0:
                    self.state = State.DATA
                else:
                    self.state = State.CHECK_SUM
                self.payload = bytearray()
            elif self.state == State.DATA:
                self.payload.append(item)
                if len(self.payload) == self.byte_count:
                    self.state = State.CHECK_SUM
            elif self.state == State.CHECK_SUM:
                self.check_sum = item
                newFrame = HartFrame(self.type,
                                     self.command_number,
                                     self.is_long_address,
                                     self.short_address,
                                     self.long_address,
                                     self.is_primary_master,
                                     self.is_burst,
                                     self.payload,
                                     self.check_sum)
                self.__queue.append(newFrame)
                isNewFrameAvailable = True
                self.__reset__()
                break

        return isNewFrameAvailable

    def dequeue(self) -> HartFrame:
        return self.__queue.pop(0)
