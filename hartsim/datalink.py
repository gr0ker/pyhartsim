import serial
import time

from .framingutils import FrameType, HartFrame, HartFrameBuilder
from .devices import CommandDispatcher

class DataLink:
    def __init__(self, port: serial.Serial, command_dispatcher: CommandDispatcher, frame_builder: HartFrameBuilder):
        self.__port = port
        self.__command_dispatcher = command_dispatcher
        self.__frame_builder = frame_builder

    def Run(self):
        self.__port.flush()
        self.__port.read_all()
        self.__port.dtr = False
        self.__port.flush()

        print(f'Listening {self.__port.name}')

        while True:
            if self.__port.in_waiting:
                data = self.__port.read_all()
                if self.__frame_builder.collect(iter(data)):
                    request = self.__frame_builder.dequeue()
                    print(f'{self.__port.name}    <= {request}')
                    status = None
                    if self.__command_dispatcher.should_dispatch(request):
                        payload, is_burst_mode = self.__command_dispatcher.dispatch(0)
                        reply = HartFrame(FrameType.ACK,
                                          request.command_number,
                                          request.is_long_address,
                                          request.short_address,
                                          request.long_address,
                                          request.is_primary_master,
                                          is_burst_mode,
                                          payload)
                        reply_data = bytearray([0xFF, 0xFF, 0xFF])
                        reply_data.extend(reply.serialize())
                        self.__port.dtr = True
                        self.__port.write(reply_data)
                        self.__port.dtr = False
                        print(
                            f'{self.__port.name} => {reply}')
                    else:
                        print(f'{self.__port.name} => None ({status})')
            else:
                time.sleep(0.01)
