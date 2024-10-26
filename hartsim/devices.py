from dataclasses import dataclass

from pydantic import BaseModel
from typing import Dict, List, Optional

from . import Payload
from .payloads import PayloadSequence

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
    request: List[Payload]
    reply: List[Payload]

@dataclass
class DeviceSpec(BaseModel):
    variables: List[VariableSpec]
    commands: List[CommandSpec]

@dataclass
class Device:
    unique_address: int
    data: Dict[str, Payload]
    commands: Dict[int, Command]
    is_burst_mode: bool = False

    def get_polling_address(self) -> int:
        return self.data['polling_address'].get_value()

    @classmethod
    def create(cls, device_spec: DeviceSpec):
        the_data: Dict[str, Payload] = { x.name: Payload.create(x.type, x.value) for x in device_spec.variables }
        the_expanded_device_type: int = the_data['expanded_device_type'].get_value()
        the_device_id: int = the_data['device_id'].get_value()
        the_unique_address = 0x3FFFFFFFFF & ((the_expanded_device_type << 24) | the_device_id)
        the_commands: Dict[int, Command] = { x.number: Command(request=PayloadSequence.create_sequence({ y.name: the_data[y.name] for y in x.request }),reply=PayloadSequence.create_sequence({ y.name: the_data[y.name] for y in x.reply })) for x in device_spec.commands }
        return cls(
            unique_address=the_unique_address,
            data=the_data,
            commands=the_commands)

class CommandDispatcher:
    def __init__(self,
                 device: Device):
        self.device = device

    def dispatch(self, number: int, request: bytearray) -> bytearray:
        if number in self.device.commands:
            self.device.data['response_code'].set_value(0)
            return list(self.device.commands[number].reply)
        else:
            self.device.data['response_code'].set_value(64)
            return list(PayloadSequence.create_sequence({ 'response_code': self.device.data['response_code'], 'device_status': self.device.data['device_status'] }))