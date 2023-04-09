from abc import abstractmethod
from functools import reduce
from itertools import repeat
from math import ceil, floor
import struct
from typing import Iterator

from attr import dataclass

FULL_BYTE_MASK = 0xFF
U16_MASK = 0xFFFF
MIN_SIZE = 1
MAX_INTEGER_SIZE = 4
BITS_IN_BYTE = 8
FLOAT_SIZE = 4
PACKED_ASCII_FALLBACK = "?"
PACKED_ASCII_FILLER = " "
PACKED_ASCII_MASK = 0x3F


class Payload:
    def __iter__(self):
        self._offset = 0
        return self

    @abstractmethod
    def __next__(self):
        pass

    @abstractmethod
    def deserialize(self, iterator: Iterator[int]):
        pass


class Unsigned(Payload):
    def __init__(self,
                 value: int = 0,
                 size: int = MIN_SIZE):
        self.__size = MIN_SIZE\
            if size < MIN_SIZE\
            else\
            MAX_INTEGER_SIZE\
            if size > MAX_INTEGER_SIZE\
            else\
            size
        self.__mask = reduce(lambda x, y: x << 8 | y,
                             repeat(FULL_BYTE_MASK, self.__size))
        self.set_value(value)

    def get_size(self):
        return self.__size

    def get_value(self):
        return self.__value

    def set_value(self, value):
        if value < 0:
            value = -value
        self.__value = value & self.__mask

    def __next__(self):
        if self._offset < self.__size:
            next = (self.__value >> (BITS_IN_BYTE *
                    (self.__size - self._offset - 1))) & FULL_BYTE_MASK
            self._offset += 1
            return next
        else:
            raise StopIteration

    def deserialize(self, iterator: Iterator[int]):
        value = 0
        for _ in range(0, self.__size):
            value = (value << BITS_IN_BYTE) | (next(iterator) & FULL_BYTE_MASK)
        self.set_value(value)


class U8(Unsigned):
    def __init__(self,
                 value: int = 0):
        super().__init__(value, 1)


class U16(Unsigned):
    def __init__(self,
                 value: int = 0):
        super().__init__(value, 2)


class U24(Unsigned):
    def __init__(self,
                 value: int = 0):
        super().__init__(value, 3)


class U32(Unsigned):
    def __init__(self,
                 value: int = 0):
        super().__init__(value, 4)


class F32(Payload):
    def __init__(self,
                 value: float = float("nan")):
        self.__size = FLOAT_SIZE
        self.set_value(value)

    def get_size(self):
        return self.__size

    def get_value(self):
        return self.__value

    def set_value(self, value):
        self.__value = value

    def __iter__(self):
        self.__serialized = struct.pack("f", self.__value)
        super().__iter__()
        return self

    def __next__(self):
        if self._offset < self.__size:
            next = self.__serialized[self.__size - self._offset - 1]
            self._offset += 1
            return next
        else:
            raise StopIteration

    def deserialize(self, iterator: Iterator[int]):
        self.__serialized = bytearray([0, 0, 0, 0])
        for i in range(0, self.__size):
            self.__serialized[i] = (next(iterator) & FULL_BYTE_MASK)
        self.set_value(struct.unpack('>f', self.__serialized))


class Ascii(Payload):
    def __init__(self,
                 size: int,
                 value: str = "",):
        self.__size = MIN_SIZE if size < MIN_SIZE else size
        self.set_value(value)

    def get_size(self):
        return self.__size

    def get_value(self) -> str:
        return self.__value

    def set_value(self, value: str):
        if (len(value) > self.__size):
            self.__value = value[:self.__size]
        else:
            self.__value = value

    def __next__(self):
        if self._offset < len(self.__value):
            next = ord(self.__value[self._offset])
            self._offset += 1
            return next
        elif self._offset < self.__size:
            next = ord(" ")
            self._offset += 1
            return next
        else:
            raise StopIteration

    def deserialize(self, iterator: Iterator[int]):
        value = ""
        for _ in range(0, self.__size):
            value += chr(next(iterator))
        self.set_value(value)


class PackedAscii(Payload):
    def __init__(self,
                 size: int,
                 value: str = "",):
        self.__size = MIN_SIZE if size < MIN_SIZE else size
        self.__packed_size = int(ceil(self.__size * 3 / 4))
        self.set_value(value)

    def get_size(self):
        return self.__size

    def get_packed_size(self):
        return self.__packed_size

    def get_value(self) -> str:
        return self.__value

    def set_value(self, value: str):
        if (len(value) > self.__size):
            newValue = value[:self.__size]
        else:
            newValue = value
        newValue = str("".join(
            map(
                lambda x: chr(ord(x) - 0x20)
                if x >= "a" and x <= "z"
                else
                PACKED_ASCII_FALLBACK
                if x < " " or x > "_"
                else
                x,
                newValue)))
        self.__value = newValue

    def __next__(self):
        if self._offset < self.__packed_size:
            left_index = floor(self._offset * 4 / 3)
            left_shift = (self._offset % 3 + 1) * 2
            right_index = left_index + 1
            right_shift = 6 - left_shift

            if left_index < self.__size:
                if left_index < len(self.__value):
                    value = self.__value[left_index]
                else:
                    value = PACKED_ASCII_FILLER
                left = ((ord(value) & PACKED_ASCII_MASK)
                        << left_shift) & FULL_BYTE_MASK
            else:
                left = 0

            if right_index < self.__size:
                if right_index < len(self.__value):
                    value = self.__value[right_index]
                else:
                    value = PACKED_ASCII_FILLER
                right = ((ord(value) & PACKED_ASCII_MASK)
                         >> right_shift) & FULL_BYTE_MASK
            else:
                right = 0

            next = left | right
            self._offset += 1
            return next
        else:
            raise StopIteration

    def deserialize(self, iterator: Iterator[int]):
        value = bytearray(self.__size)
        for i in range(0, self.__packed_size):
            item = next(iterator)

            left_index = floor(i * 4 / 3)
            left_shift = (i % 3 + 1) * 2

            if left_index < self.__size:
                value[left_index] |= (item >> left_shift) & PACKED_ASCII_MASK

            right_index = left_index + 1
            right_shift = 6 - left_shift

            if right_index < self.__size:
                value[right_index] |= (item << right_shift) & PACKED_ASCII_MASK

        value = bytearray(
            [item + 0x40 if item < 0x20 else item for item in value])

        self.set_value(str(value, "ascii"))


@dataclass
class PayloadSequence(Payload):
    def __iter__(self):
        self.__attr_iterator = iter(
            filter(lambda x: not x.startswith("_"), list(self.__dict__.keys())))
        self.__byte_iterator = iter(self.__dict__[next(self.__attr_iterator)])
        return self

    def __next__(self):
        try:
            result = next(self.__byte_iterator)
        except StopIteration:
            self.__byte_iterator = iter(
                self.__dict__[next(self.__attr_iterator)])
            result = next(self.__byte_iterator)
        return result

    def deserialize(self, iterator: Iterator[int]):
        for attr in self.__dict__.keys():
            self.__dict__[attr].deserialize(iterator)
