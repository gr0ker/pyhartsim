import serial
import time

from .config import Configuration
from .framingutils import FrameType, HartFrame, HartFrameBuilder
from .commands import handle_request
from .devices import HartDevice
from .payloads import U8, U16, U24, Ascii, PackedAscii

config = Configuration()

port = serial.Serial(config.port,
                     baudrate=1200,
                     parity=serial.PARITY_ODD,
                     bytesize=8,
                     stopbits=1)

port.flush()
port.read_all()
port.dtr = False

print(f'Listening {config.port}')

frameBuilder = HartFrameBuilder()

device3051 = HartDevice(
    polling_address=U8(0),
    long_address=0x3FFFFFFFFF & 0x2606123456,
    expanded_device_type=U16(0x2606),
    device_id=U24(0x123456),
    hart_tag=PackedAscii(8, "3051 r10"),
    hart_long_tag=Ascii(32, "This is 3051 rev 10             "))

device150 = HartDevice(
    universal_revision=U8(5),
    polling_address=U8(1),
    long_address=0x3FFFFFFFFF & 0x9979789ABC,
    expanded_device_type=U16(0x9979),
    device_id=U24(0x789ABC),
    hart_tag=PackedAscii(8, "150 r10 "),
    hart_long_tag=Ascii(32, "This is 150 rev 10              "))

poll_map = {
    device3051.polling_address.get_value(): device3051,
    device150.polling_address.get_value(): device150
}

unique_map = {
    device3051.long_address: device3051,
    device150.long_address: device150
}

for short_address in poll_map:
    print(
        f'  Address #{short_address}: \
Type=0x{poll_map[short_address].expanded_device_type.get_value():04X}, \
ID=0x{poll_map[short_address].device_id.get_value():06X}')

while True:
    if port.in_waiting:
        data = port.read_all()
        if frameBuilder.collect(iter(data)):
            request = frameBuilder.dequeue()
            print(f'{config.port}    <= {request}')
            device = None
            if request.is_long_address:
                if request.long_address in unique_map:
                    device = unique_map[request.long_address]
            else:
                if request.short_address in poll_map:
                    device = poll_map[request.short_address]
            if device is not None:
                payload = handle_request(
                    device, request.command_number, request.data)
                reply = HartFrame(FrameType.ACK,
                                  request.command_number,
                                  request.is_long_address,
                                  device.polling_address.get_value(),
                                  device.long_address,
                                  request.is_primary_master,
                                  device.is_burst_mode,
                                  payload)
                reply_data = bytearray([0xFF, 0xFF, 0xFF])
                reply_data.extend(reply.serialize())
                port.dtr = True
                port.write(reply_data)
                port.dtr = False
                print(
                    f'{config.port} #{device.polling_address.get_value()} => {reply}')
            else:
                print(f'{config.port} => None')
    else:
        time.sleep(0.01)
