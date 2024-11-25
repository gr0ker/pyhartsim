import serial
import time

from .config import Configuration
from .framingutils import FrameType, HartFrame, HartFrameBuilder
from .commands import handle_request
from .devices import DeviceVariable, HartDevice
from .payloads import F32, U8, U16, U24, Ascii, PackedAscii

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
    device_variables={
        0: DeviceVariable(U8(12), U8(12), F32(1.2345), U8(65), U8(192)),
        1: DeviceVariable(U8(32), U8(32), F32(23.456), U8(0), U8(192)),
        2: DeviceVariable(U8(244), U8(244), F32(45.67), U8(0), U8(192)),
        3: DeviceVariable(U8(242), U8(242), F32(4567.8), U8(0), U8(192)),
        4: DeviceVariable(U8(45), U8(45), F32(5.6789), U8(0), U8(192)),
        5: DeviceVariable(U8(41), U8(41), F32(67.890), U8(0), U8(192)),
        6: DeviceVariable(U8(244), U8(244), F32(67.890), U8(0), U8(192)),
        7: DeviceVariable(U8(244), U8(244), F32(67.890), U8(0), U8(192)),
        8: DeviceVariable(U8(244), U8(244), F32(67.890), U8(0), U8(192)),
        9: DeviceVariable(U8(244), U8(244), F32(67.890), U8(0), U8(192)),
        244: DeviceVariable(U8(57), U8(57), F32(56.7890), U8(0), U8(192)),
        245: DeviceVariable(U8(39), U8(39), F32(4.5678), U8(0), U8(192)),
        246: DeviceVariable(U8(12), U8(12), F32(1.2345), U8(65), U8(192)),
        247: DeviceVariable(U8(32), U8(32), F32(23.456), U8(0), U8(192)),
        248: DeviceVariable(U8(241), U8(241), F32(345.67), U8(0), U8(192)),
        249: DeviceVariable(U8(244), U8(244), F32(4567.8), U8(0), U8(192)),
    },
    dynamic_variables={
        0: 0,
        1: 1,
        2: 2,
        3: 3,
    },
    polling_address=U8(0),
    # long_address=0x3FFFFFFFFF & 0x268F123456,
    # expanded_device_type=U16(0x268F),
    long_address=0x3FFFFFFFFF & 0xf9f5123456,
    expanded_device_type=U16(0xf9f5),
    device_id=U24(0x123456),
    hart_tag=PackedAscii(8, "3051 r10"),
    hart_long_tag=Ascii(32, "This is 3051 rev 10             "),
    device_status=U8(0x10))

device150 = HartDevice(
    device_variables={
        0: DeviceVariable(U8(12), U8(12), F32(1.2345), U8(65), U8(192)),
        1: DeviceVariable(U8(32), U8(32), F32(23.456), U8(0), U8(192)),
        244: DeviceVariable(U8(57), U8(57), F32(56.7890), U8(0), U8(192)),
        245: DeviceVariable(U8(39), U8(39), F32(4.5678), U8(0), U8(192)),
        246: DeviceVariable(U8(12), U8(12), F32(1.2345), U8(65), U8(192)),
        247: DeviceVariable(U8(32), U8(32), F32(23.456), U8(0), U8(192)),
        248: DeviceVariable(U8(32), U8(32), F32(23.456), U8(0), U8(192)),
        249: DeviceVariable(U8(32), U8(32), F32(23.456), U8(0), U8(192)),
    },
    dynamic_variables={
        0: 0,
        1: 1,
        2: 1,
        3: 1,
    },
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

port.flush()

while True:
    if port.in_waiting:
        data = port.read_all()
        if frameBuilder.collect(iter(data)):
            request = frameBuilder.dequeue()
            print(f'{config.port}    <= {request}')
            device = None
            status = None
            if request.is_long_address:
                if request.long_address in unique_map:
                    device = unique_map[request.long_address]
                else:
                    status =\
                        f'Long address 0x{request.long_address:010X} does not match'
            else:
                if request.short_address in poll_map:
                    device = poll_map[request.short_address]
                else:
                    status =\
                        f'Polling address {request.short_address} does not match'
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
                print(f'{config.port} => None ({status})')
    else:
        time.sleep(0.01)
