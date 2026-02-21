import unittest
import tempfile
import os
from functools import reduce

from hartsim.logparser import (
    strip_preambles, parse_log_file, LogResponseProvider,
    _build_frame, _parse_fdi_hex, FDI_FRAME_PATTERN,
)


class TestLogParser(unittest.TestCase):

    def test_strip_preambles_removes_leading_ff(self):
        data = bytes.fromhex('FFFFFFFFFF0280000082')
        expected = bytes.fromhex('0280000082')
        self.assertEqual(strip_preambles(data), expected)

    def test_strip_preambles_no_preambles(self):
        data = bytes.fromhex('0280000082')
        expected = bytes.fromhex('0280000082')
        self.assertEqual(strip_preambles(data), expected)

    def test_strip_preambles_all_preambles(self):
        data = bytes.fromhex('FFFFFFFFFFFF')
        expected = bytes()
        self.assertEqual(strip_preambles(data), expected)

    def test_strip_preambles_empty(self):
        data = bytes()
        expected = bytes()
        self.assertEqual(strip_preambles(data), expected)

    def test_parse_log_file_single_pair(self):
        log_content = '''[2026-02-03 15:52:36.867 +05:00 DBG  #] Master MAC on ("COM15") Tx: time 86.1 data "FFFFFFFFFF0280000082"
[2026-02-03 15:52:37.192 +05:00 DBG  #] RCV_MSG ("COM15"): time 294.9 (ACK) 4+29 bytes "068000180000FE996C050701"'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(log_content)
            temp_path = f.name

        try:
            result = parse_log_file(temp_path)
            request = bytes.fromhex('0280000082')
            response = bytes.fromhex('068000180000FE996C050701')

            self.assertIn(request, result)
            self.assertEqual(len(result[request]), 1)
            self.assertEqual(result[request][0], response)
        finally:
            os.unlink(temp_path)

    def test_parse_log_file_request_without_response(self):
        log_content = '''[2026-02-03 15:52:36.867 +05:00 DBG  #] Master MAC on ("COM15") Tx: time 86.1 data "FFFFFFFFFF0280000082"
[2026-02-03 15:52:37.000 +05:00 INF  #] Some other log line
[2026-02-03 15:52:37.100 +05:00 DBG  #] Master MAC on ("COM15") Tx: time 87.0 data "FFFFFFFFFF0281000083"
[2026-02-03 15:52:37.500 +05:00 DBG  #] RCV_MSG ("COM15"): time 294.9 (ACK) 4+29 bytes "068100180000FE996C050702"'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(log_content)
            temp_path = f.name

        try:
            result = parse_log_file(temp_path)
            # First request has no response (next line was another TX)
            request1 = bytes.fromhex('0280000082')
            self.assertNotIn(request1, result)

            # Second request has response
            request2 = bytes.fromhex('0281000083')
            response2 = bytes.fromhex('068100180000FE996C050702')
            self.assertIn(request2, result)
            self.assertEqual(result[request2][0], response2)
        finally:
            os.unlink(temp_path)

    def test_parse_log_file_multiple_responses_same_request(self):
        log_content = '''[2026-02-03 15:52:36.000 +05:00 DBG  #] Master MAC on ("COM15") Tx: time 86.1 data "FFFFFFFFFF0280000082"
[2026-02-03 15:52:36.300 +05:00 DBG  #] RCV_MSG ("COM15"): time 294.9 (ACK) 4+5 bytes "0680001800AA"
[2026-02-03 15:52:37.000 +05:00 DBG  #] Master MAC on ("COM15") Tx: time 86.1 data "FFFFFFFFFF0280000082"
[2026-02-03 15:52:37.300 +05:00 DBG  #] RCV_MSG ("COM15"): time 294.9 (ACK) 4+5 bytes "0680001800BB"
[2026-02-03 15:52:38.000 +05:00 DBG  #] Master MAC on ("COM15") Tx: time 86.1 data "FFFFFFFFFF0280000082"
[2026-02-03 15:52:38.300 +05:00 DBG  #] RCV_MSG ("COM15"): time 294.9 (ACK) 4+5 bytes "0680001800CC"'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(log_content)
            temp_path = f.name

        try:
            result = parse_log_file(temp_path)
            request = bytes.fromhex('0280000082')

            self.assertIn(request, result)
            self.assertEqual(len(result[request]), 3)
            self.assertEqual(result[request][0], bytes.fromhex('0680001800AA'))
            self.assertEqual(result[request][1], bytes.fromhex('0680001800BB'))
            self.assertEqual(result[request][2], bytes.fromhex('0680001800CC'))
        finally:
            os.unlink(temp_path)

    def test_parse_log_file_skips_non_matching_lines(self):
        log_content = '''[2026-02-03 15:51:46.397 +05:00 INF  #] Now listening on: "http://0.0.0.0:9000"
[2026-02-03 15:51:52.024 +05:00 INF  #] Request starting "HTTP/1.1" "GET"
[2026-02-03 15:52:36.867 +05:00 DBG  #] Master MAC on ("COM15") Tx: time 86.1 data "FFFFFFFFFF0280000082"
[2026-02-03 15:52:37.192 +05:00 DBG  #] RCV_MSG ("COM15"): time 294.9 (ACK) 4+5 bytes "068000180001"
[2026-02-03 15:52:38.000 +05:00 INF  #] Some info log'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(log_content)
            temp_path = f.name

        try:
            result = parse_log_file(temp_path)
            self.assertEqual(len(result), 1)
            request = bytes.fromhex('0280000082')
            self.assertIn(request, result)
        finally:
            os.unlink(temp_path)


class TestLogResponseProvider(unittest.TestCase):

    def test_get_response_returns_matching_response(self):
        request = bytes.fromhex('0280000082')
        response = bytes.fromhex('068000180001')
        request_responses = {request: [response]}

        provider = LogResponseProvider(request_responses)
        result = provider.get_response(request)

        self.assertEqual(result, response)

    def test_get_response_returns_none_for_unknown_request(self):
        request = bytes.fromhex('0280000082')
        response = bytes.fromhex('068000180001')
        request_responses = {request: [response]}

        provider = LogResponseProvider(request_responses)
        unknown_request = bytes.fromhex('0281000083')
        result = provider.get_response(unknown_request)

        self.assertIsNone(result)

    def test_get_response_round_robin(self):
        request = bytes.fromhex('0280000082')
        responses = [
            bytes.fromhex('068000180001'),
            bytes.fromhex('068000180002'),
            bytes.fromhex('068000180003'),
        ]
        request_responses = {request: responses}

        provider = LogResponseProvider(request_responses)

        # First round
        self.assertEqual(provider.get_response(request), responses[0])
        self.assertEqual(provider.get_response(request), responses[1])
        self.assertEqual(provider.get_response(request), responses[2])

        # Wraps around
        self.assertEqual(provider.get_response(request), responses[0])
        self.assertEqual(provider.get_response(request), responses[1])

    def test_get_request_count(self):
        request_responses = {
            bytes.fromhex('0280000082'): [bytes.fromhex('01')],
            bytes.fromhex('0281000083'): [bytes.fromhex('02')],
            bytes.fromhex('0282000084'): [bytes.fromhex('03')],
        }
        provider = LogResponseProvider(request_responses)
        self.assertEqual(provider.get_request_count(), 3)

    def test_get_total_response_count(self):
        request_responses = {
            bytes.fromhex('0280000082'): [bytes.fromhex('01'), bytes.fromhex('02')],
            bytes.fromhex('0281000083'): [bytes.fromhex('03')],
        }
        provider = LogResponseProvider(request_responses)
        self.assertEqual(provider.get_total_response_count(), 3)


class TestFdiParsing(unittest.TestCase):

    def test_parse_fdi_hex(self):
        self.assertEqual(_parse_fdi_hex('00-50-FE'), bytes([0x00, 0x50, 0xFE]))
        self.assertEqual(_parse_fdi_hex('AB'), bytes([0xAB]))

    def test_build_frame_short_address_request(self):
        # POL(0) CMD(0) — short address request
        match = FDI_FRAME_PATTERN.search('POL(0) CMD(0)')
        frame = _build_frame(match, is_response=False)
        # delimiter=0x02, address=0x80 (primary master + addr 0), cmd=0, bytecount=0, checksum
        expected = bytearray([0x02, 0x80, 0x00, 0x00])
        expected.append(reduce(lambda x, y: x ^ y, expected))
        self.assertEqual(frame, bytes(expected))

    def test_build_frame_short_address_response(self):
        # POL(0) CMD(0) DAT(00-50-FE-26-4A) — short address response
        match = FDI_FRAME_PATTERN.search('POL(0) CMD(0) DAT(00-50-FE-26-4A)')
        frame = _build_frame(match, is_response=True)
        data = bytes([0x00, 0x50, 0xFE, 0x26, 0x4A])
        expected = bytearray([0x06, 0x00, 0x00, len(data)])
        expected.extend(data)
        expected.append(reduce(lambda x, y: x ^ y, expected))
        self.assertEqual(frame, bytes(expected))

    def test_build_frame_long_address_request(self):
        # TYP(0x264A) UID(0x2DC704) CMD(128)
        match = FDI_FRAME_PATTERN.search('TYP(0x264A) UID(0x2DC704) CMD(128)')
        frame = _build_frame(match, is_response=False)
        # delimiter=0x82, address: first byte = (0x26>>0)&0x3F | 0x80 = 0x26|0x80 = 0xA6
        # device_type = 0x264A: high byte = 0x26, low byte = 0x4A
        # device_id = 0x2DC704
        expected = bytearray([0x82, 0xA6, 0x4A, 0x2D, 0xC7, 0x04, 128, 0x00])
        expected.append(reduce(lambda x, y: x ^ y, expected))
        self.assertEqual(frame, bytes(expected))

    def test_build_frame_long_address_response_with_data(self):
        # TYP(0x264A) UID(0x2DC704) CMD(0) DAT(00-50-FE)
        match = FDI_FRAME_PATTERN.search('TYP(0x264A) UID(0x2DC704) CMD(0) DAT(00-50-FE)')
        frame = _build_frame(match, is_response=True)
        data = bytes([0x00, 0x50, 0xFE])
        expected = bytearray([0x86, 0x26, 0x4A, 0x2D, 0xC7, 0x04, 0x00, len(data)])
        expected.extend(data)
        expected.append(reduce(lambda x, y: x ^ y, expected))
        self.assertEqual(frame, bytes(expected))

    def test_build_frame_with_request_data(self):
        # TYP(0x264A) UID(0x2DC704) CMD(33) DAT(00-01-02-03)
        match = FDI_FRAME_PATTERN.search('TYP(0x264A) UID(0x2DC704) CMD(33) DAT(00-01-02-03)')
        frame = _build_frame(match, is_response=False)
        data = bytes([0x00, 0x01, 0x02, 0x03])
        expected = bytearray([0x82, 0xA6, 0x4A, 0x2D, 0xC7, 0x04, 33, len(data)])
        expected.extend(data)
        expected.append(reduce(lambda x, y: x ^ y, expected))
        self.assertEqual(frame, bytes(expected))

    def test_parse_fdi_log_file(self):
        log_content = (
            '[2025-06-23 15:37:45.617 +05:00 INF  #] Sending "POL(0) CMD(0)"\n'
            '[2025-06-23 15:37:46.101 +05:00 INF  #] Received "FrameTransmissionResult '
            '{ Status = Success, Response = POL(0) CMD(0) '
            'DAT(00-50-FE-26-4A-05-05-01-06-08-00-2D-C7-04) }"\n'
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
            f.write(log_content)
            temp_path = f.name

        try:
            result = parse_log_file(temp_path)
            self.assertEqual(len(result), 1)

            # Verify request frame was built correctly
            request_keys = list(result.keys())
            request = request_keys[0]
            # Short address: delimiter=0x02, addr=0x80, cmd=0, bc=0, checksum
            self.assertEqual(request[0], 0x02)  # STX
            self.assertEqual(request[1], 0x80)  # primary master, addr 0
            self.assertEqual(request[2], 0x00)  # cmd 0

            # Verify response frame
            responses = result[request]
            self.assertEqual(len(responses), 1)
            self.assertEqual(responses[0][0], 0x06)  # ACK
        finally:
            os.unlink(temp_path)

    def test_parse_fdi_log_file_long_address(self):
        log_content = (
            '[2025-06-23 15:38:09.119 +05:00 INF  #] Sending "TYP(0x264A) UID(0x2DC704) CMD(128)"\n'
            '[2025-06-23 15:38:09.120 +05:00 INF  #] Sending "TYP(0x264A) UID(0x2DC704) CMD(128)"\n'
            '[2025-06-23 15:38:09.676 +05:00 INF  #] Received "FrameTransmissionResult '
            '{ Status = Success, Response = TYP(0x264A) UID(0x2DC704) CMD(128) '
            'DAT(00-50-0D-02-0A-02-FB-FB-FB-FB-01-02-00-02-00-00-07-10) }"\n'
            '[2025-06-23 15:38:09.677 +05:00 INF  #] Received "TYP(0x264A) UID(0x2DC704) CMD(128) '
            'DAT(00-50-0D-02-0A-02-FB-FB-FB-FB-01-02-00-02-00-00-07-10)" (Success)\n'
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
            f.write(log_content)
            temp_path = f.name

        try:
            result = parse_log_file(temp_path)
            # Duplicate Sending lines -> only one unique request
            self.assertEqual(len(result), 1)

            request = list(result.keys())[0]
            self.assertEqual(request[0], 0x82)  # STX long
            self.assertEqual(request[6], 128)   # cmd 128

            # Only FrameTransmissionResult response counted, not the simple Received echo
            responses = result[request]
            self.assertEqual(len(responses), 1)
        finally:
            os.unlink(temp_path)

    def test_parse_fdi_log_skips_non_matching_lines(self):
        log_content = (
            '[2025-06-23 15:37:24.515 +05:00 WRN  #] Overriding address(es).\n'
            '[2025-06-23 15:37:24.584 +05:00 INF  #] Now listening on: "http://0.0.0.0:9000"\n'
            '[2025-06-23 15:37:45.617 +05:00 INF  #] Sending "POL(0) CMD(0)"\n'
            '[2025-06-23 15:37:46.101 +05:00 INF  #] Received "FrameTransmissionResult '
            '{ Status = Success, Response = POL(0) CMD(0) DAT(00-50) }"\n'
            '[2025-06-23 15:37:50.312 +05:00 WRN  #] Invalid frame received\n'
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
            f.write(log_content)
            temp_path = f.name

        try:
            result = parse_log_file(temp_path)
            self.assertEqual(len(result), 1)
        finally:
            os.unlink(temp_path)

    def test_parse_fdi_log_request_without_response(self):
        log_content = (
            '[2025-06-23 15:37:45.617 +05:00 INF  #] Sending "POL(0) CMD(0)"\n'
            '[2025-06-23 15:37:50.312 +05:00 WRN  #] Invalid frame received\n'
            '[2025-06-23 15:37:50.314 +05:00 INF  #] Sending "POL(1) CMD(0)"\n'
            '[2025-06-23 15:37:53.921 +05:00 WRN  #] Invalid frame received\n'
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
            f.write(log_content)
            temp_path = f.name

        try:
            result = parse_log_file(temp_path)
            self.assertEqual(len(result), 0)
        finally:
            os.unlink(temp_path)

    def test_checksum_valid(self):
        # Verify that built frames have valid checksums (XOR of all preceding bytes)
        match = FDI_FRAME_PATTERN.search('TYP(0x264A) UID(0x2DC704) CMD(0) DAT(00-50-FE)')
        frame = _build_frame(match, is_response=True)
        self.assertEqual(reduce(lambda x, y: x ^ y, frame), 0)


if __name__ == '__main__':
    unittest.main()
