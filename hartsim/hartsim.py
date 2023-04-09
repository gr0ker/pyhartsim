import serial
import time

from .config import Configuration
from .framingutils import FrameType, HartFrame
from .payloads import U8
from .commands import Cmd0Reply, Cmd1Reply, Cmd20Reply, ErrorReply, long_address,\
    short_address, is_burst_mode

config = Configuration()

port = serial.Serial(config.port,
                     baudrate=1200,
                     parity=serial.PARITY_ODD,
                     bytesize=8,
                     stopbits=1)

port.flush()
port.read_all()


while True:
    if port.in_waiting:
        data = port.read_all()
        request = HartFrame.deserialize(iter(data))
        print(f'<= {request}')
        long_address_matched = request.is_long_address\
            and request.long_address == long_address
        short_address_matched = not request.is_long_address\
            and request.short_address == short_address
        if long_address_matched or short_address_matched:
            if request.command_number == 0:
                payload = Cmd0Reply()
            elif request.command_number == 1:
                payload = Cmd1Reply()
            elif request.command_number == 20:
                payload = Cmd20Reply()
            else:
                payload = ErrorReply(response_code=U8(64))
            reply = HartFrame(FrameType.ACK,
                              request.command_number,
                              request.is_long_address,
                              short_address,
                              long_address,
                              request.is_primary_master,
                              is_burst_mode,
                              list(payload))
            reply_data = bytearray([0xFF, 0xFF, 0xFF])
            reply_data.extend(reply.to_bytes())
            port.write(reply_data)
            print(f'=> {reply}')
        else:
            print('=> None')
    else:
        time.sleep(0.01)
