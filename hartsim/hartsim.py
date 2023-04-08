from dataclasses import dataclass
from types import FrameType
import serial
import time
from hartsim import HartFrame, U16, U24, U8, PayloadSequence

port = serial.Serial('COM3', baudrate=1200,
                     parity=serial.PARITY_ODD, bytesize=8, stopbits=1)
port.flush()

short_address = 0
long_address = bytearray([0x19, 0x73, 0x17, 0xE7, 0x19])
is_burst_mode = False

expanded_device_type = U16(0x2606)
device_id: U24 = U24(0x123456)
device_status = U8()
extended_device_status = U8()
config_change_counter = U16(0)


@dataclass
class Cmd0Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    expansion_code: U8 = U8(254)
    expanded_device_type: U16 = expanded_device_type
    request_preambles: U8 = U8(5)
    universal_revision: U8 = U8(7)
    device_revision: U8 = U8(10)
    software_revision: U8 = U8(3)
    hardware_revision_signaling_code: U8 = U8(0x64)
    flags: U8 = U8()
    device_id: U24 = device_id
    response_preambles: U8 = U8(5)
    max_device_variables: U8 = U8(1)
    config_change_counter: U16 = config_change_counter
    extended_device_status: U8 = extended_device_status
    manufacturer_code: U16 = U16(0x0026)
    private_label_distributor: U16 = U16(0x0026)
    device_profile: U8 = U8()


@dataclass
class ErrorReply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status


while True:
    if port.in_waiting:
        data = port.read_all()
        print(data)
        request = HartFrame.deserialize(iter(data))
        print(f'Received {request}')
        if request.is_long_address and request.long_address == long_address or not request.is_long_address and request.short_address == short_address:
            if request.command_number == 0:
                payload = Cmd0Reply()
            else:
                payload = ErrorReply(response_code=64)
            reply = HartFrame(FrameType.ACK,
                              request.command_number,
                              request.is_long_address,
                              short_address,
                              long_address,
                              request.is_primary_master,
                              is_burst_mode,
                              list(payload))
            print(f'Reply {reply}')
            reply_data = bytearray([0xFF, 0xFF, 0xFF])
            reply_data.extend(reply.to_bytes())
            print(reply_data)
            port.write(reply_data)
    else:
        print('No reply required')
        time.sleep(0.01)
