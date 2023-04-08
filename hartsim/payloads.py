from abc import abstractmethod
from functools import reduce
from itertools import repeat
from typing import Iterator

from attr import dataclass

FULL_BYTE_MASK = 0xFF
U16_MASK = 0xFFFF
MIN_INTEGER_SIZE = 1
MAX_INTEGER_SIZE = 4
BITS_IN_BYTE = 8


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
                 size: int = MIN_INTEGER_SIZE):
        self.__size = MIN_INTEGER_SIZE if size < MIN_INTEGER_SIZE else MAX_INTEGER_SIZE if size > MAX_INTEGER_SIZE else size
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
