import unittest
import tempfile
import os

from hartsim.logparser import strip_preambles, parse_log_file, LogResponseProvider


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


if __name__ == '__main__':
    unittest.main()
