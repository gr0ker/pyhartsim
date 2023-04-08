from abc import abstractmethod
from typing import Iterator

FULL_BYTE_MASK = 0xFF


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


class U8(Payload):
    def __init__(self,
                 value: int = 0):
        self.set_value(value)

    def get_value(self):
        return self.__value

    def set_value(self, value):
        if value < 0:
            value = -value
        self.__value = value & FULL_BYTE_MASK

    def __next__(self):
        if self._offset == 0:
            self._offset += 1
            return self.__value & FULL_BYTE_MASK
        else:
            raise StopIteration

    def deserialize(self, iterator: Iterator[int]):
        self.set_value(next(iterator) & FULL_BYTE_MASK)
