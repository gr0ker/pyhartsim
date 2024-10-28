from dataclasses import dataclass
import json
from pydantic import BaseModel
from typing import cast, Dict, List, Optional

from . import Payload, HartFrame
from .payloads import U8, U16, U24, PayloadSequence

@dataclass
class VariableSpec:
    name: str
    type: str
    value: Optional[object] = None

@dataclass
class ReferenceSpec:
    name: str

@dataclass
class CommandSpec:
    number: int
    request: List[ReferenceSpec]
    reply: List[ReferenceSpec]

@dataclass
class Command:
    request: PayloadSequence
    reply: PayloadSequence

@dataclass
class DeviceSpec(BaseModel):
    variables: List[VariableSpec]
    commands: List[CommandSpec]

    @classmethod
    def load(cls, path: str):
        data_file = open(path)
        try:
            device_data = json.load(data_file)
        finally:
            data_file.close()

        return DeviceSpec.model_validate(device_data)

def raise_exception(ex): raise ex

@dataclass
class Device:
    unique_address: int
    data: Dict[str, Payload]
    commands: Dict[int, Command]
    is_burst_mode: bool = False

    def get_polling_address(self) -> int:
        return cast(U8, self.data['polling_address']).get_value()\
            if isinstance(self.data['polling_address'], U8)\
            else raise_exception(TypeError("expanded_device_type must be U16"))

    @classmethod
    def create(cls, device_spec: DeviceSpec):
        the_data: Dict[str, Payload] = { x.name: Payload.create(x.type, x.value) for x in device_spec.variables }
        if isinstance(the_data['expanded_device_type'], U16):
            the_expanded_device_type: int = cast(U16, the_data['expanded_device_type']).get_value()
        else:
            raise TypeError("expanded_device_type must be U16")
        if isinstance(the_data['device_id'], U24):
            the_device_id: int = cast(U24, the_data['device_id']).get_value()
        else:
            raise TypeError("device_id must be U24")
        the_unique_address = 0x3FFFFFFFFF & ((the_expanded_device_type << 24) | the_device_id)
        the_commands: Dict[int, Command] = {
            x.number: Command(
                request=PayloadSequence.create_sequence({ y.name: the_data[y.name] for y in x.request }),
                reply=PayloadSequence.create_sequence({ y.name: the_data[y.name] for y in x.reply }))\
            for x in device_spec.commands
        }
        return cls(
            unique_address=the_unique_address,
            data=the_data,
            commands=the_commands)

class CommandDispatcher:
    def __init__(self,
                 device: Device):
        self.__device = device

    def should_dispatch(self, request: HartFrame) -> bool:
        return request.is_long_address and request.long_address == self.__device.unique_address\
            or not request.is_long_address and request.command_number == 0\
            and request.short_address == self.__device.get_polling_address()


    def dispatch(self, number: int) -> tuple[bytearray, bool]:
        if isinstance(self.__device.data['response_code'], U8):
            the_response_code: U8 = cast(U8, self.__device.data['response_code'])
        else:
            raise TypeError("device_id must be U24")
        if number in self.__device.commands:
            the_response_code.set_value(0)
            return self.__device.commands[number].reply.serialize(), self.__device.is_burst_mode
        else:
            the_response_code.set_value(64)
            error_reply = PayloadSequence.create_sequence({
                'response_code': self.__device.data['response_code'],
                'device_status': self.__device.data['device_status']
            })
            return error_reply.serialize(), self.__device.is_burst_mode