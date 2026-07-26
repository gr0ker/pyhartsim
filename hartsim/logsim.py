import argparse
import sys
import time

import serial

from .config import Configuration
from .framingutils import HartFrameBuilder
from .logparser import parse_log_file, LogResponseProvider

PREAMBLE_COUNT = 5


def main():
    parser = argparse.ArgumentParser(
        prog='python -m hartsim.logsim',
        description='Replay a recorded HART communication log over a serial port.')
    parser.add_argument('logfile', help='path to the recorded log file')
    parser.add_argument('--port', default=None,
                        help='serial port name (default: HARTSIM_PORT env var or COM2)')
    args = parser.parse_args()

    log_file = args.logfile
    print(f'Loading log file: {log_file}')

    try:
        request_responses = parse_log_file(log_file)
    except FileNotFoundError:
        print(f'Error: Log file not found: {log_file}')
        sys.exit(1)
    except Exception as e:
        print(f'Error parsing log file: {e}')
        sys.exit(1)

    provider = LogResponseProvider(request_responses)
    print(f'Loaded {provider.get_request_count()} unique requests, '
          f'{provider.get_total_response_count()} total responses')

    if provider.get_request_count() == 0:
        print('Warning: No request/response pairs found in log file')

    config = Configuration()
    if args.port:
        config.port = args.port
    port = serial.Serial(config.port,
                         baudrate=1200,
                         parity=serial.PARITY_ODD,
                         bytesize=8,
                         stopbits=1)

    port.flush()
    port.read_all()
    port.dtr = False

    print(f'Listening on {config.port}')

    frame_builder = HartFrameBuilder()

    while True:
        if port.in_waiting:
            data = port.read_all()
            if frame_builder.collect(iter(data)):
                frame = frame_builder.dequeue()
                request = bytes(frame.serialize())
                request_hex = request.hex().upper()
                response, is_fallback = provider.get_response(request)

                if response is not None:
                    # Prepend preambles and send response
                    preambles = bytes([0xFF] * PREAMBLE_COUNT)
                    reply_data = preambles + response

                    port.dtr = True
                    port.write(reply_data)
                    port.flush()
                    port.dtr = False

                    response_hex = response.hex().upper()
                    match_type = ' (fallback)' if is_fallback else ''
                    print(f'{config.port} <= {request_hex}')
                    print(f'{config.port} => {response_hex}{match_type}')
                else:
                    print(f'{config.port} <= {request_hex} (no match)')
        else:
            time.sleep(0.01)


if __name__ == '__main__':
    main()
