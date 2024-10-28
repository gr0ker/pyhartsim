import json
import serial

from .config import Configuration
from .datalink import DataLink
from .framingutils import HartFrameBuilder
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

frame_builder = HartFrameBuilder()

data_link = DataLink(port, command_dispatcher, frame_builder)

data_link.Run()