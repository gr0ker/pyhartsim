import json
import serial
import time

from .config import Configuration
from .framingutils import FrameType, HartFrame, HartFrameBuilder
from .devices import DeviceSpec, Device, CommandDispatcher

config_file = open('config/config.json')
try:
    config_data = json.load(config_file)
finally:
    config_file.close()

config = Configuration.from_dict(config_data)

data_file = open('data/000099.9972.0701.json')
try:
    device_data = json.load(data_file)
finally:
    data_file.close()

device_spec = DeviceSpec.model_validate(device_data)
device = Device.create(device_spec)
print(device)
print(f"Polling address: #{device.get_polling_address()}")
print(f"Unique address: 0x{device.unique_address:010X}")

command_dispatcher = CommandDispatcher(device)

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

port.flush()

while True:
    if port.in_waiting:
        data = port.read_all()
        if frameBuilder.collect(iter(data)):
            request = frameBuilder.dequeue()
            print(f'{config.port}    <= {request}')
            status = None
            if request.is_long_address and request.long_address == device.unique_address\
                    or not request.is_long_address and request.command_number == 0\
                    and request.short_address == device.get_polling_address():
                payload = command_dispatcher.dispatch(0)
                reply = HartFrame(FrameType.ACK,
                                  request.command_number,
                                  request.is_long_address,
                                  device.get_polling_address(),
                                  device.unique_address,
                                  request.is_primary_master,
                                  device.is_burst_mode,
                                  payload)
                reply_data = bytearray([0xFF, 0xFF, 0xFF])
                reply_data.extend(reply.serialize())
                port.dtr = True
                port.write(reply_data)
                port.dtr = False
                print(
                    f'{config.port} #{device.get_polling_address()} => {reply}')
            else:
                print(f'{config.port} => None ({status})')
    else:
        time.sleep(0.01)
