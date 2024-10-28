from .config import Configuration
from .datalink import create_port, DataLink
from .framingutils import HartFrameBuilder
from .devices import DeviceSpec, Device, CommandDispatcher

config = Configuration.load('config/config.json')
device_spec = DeviceSpec.load('data/000099.9972.0701.json')
device = Device.create(device_spec)

print(f"Polling address: #{device.get_polling_address()}")
print(f"Unique address: 0x{device.unique_address:010X}")

port = create_port(config.port)
command_dispatcher = CommandDispatcher(device)
frame_builder = HartFrameBuilder()
data_link = DataLink(port, command_dispatcher, frame_builder)
data_link.Run()