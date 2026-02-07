import re
from typing import Dict, List


# Regex patterns for log parsing
TX_PATTERN = re.compile(r'Master MAC on \("[^"]+"\) Tx: time [\d.]+ data "([0-9A-Fa-f]+)"')
RX_PATTERN = re.compile(r'RCV_MSG \("[^"]+"\): time [\d.]+ \(ACK\) \d+\+\d+ bytes "([0-9A-Fa-f]+)"')


def strip_preambles(data: bytes) -> bytes:
    """Strip leading 0xFF preamble bytes from frame data."""
    i = 0
    while i < len(data) and data[i] == 0xFF:
        i += 1
    return data[i:]


def parse_log_file(file_path: str) -> Dict[bytes, List[bytes]]:
    """
    Parse a HART communication log file and extract request/response pairs.

    Args:
        file_path: Path to the log file

    Returns:
        Dictionary mapping request frames (preambles stripped) to lists of response frames
    """
    request_responses: Dict[bytes, List[bytes]] = {}
    pending_request: bytes | None = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Try to match a request line
            tx_match = TX_PATTERN.search(line)
            if tx_match:
                hex_data = tx_match.group(1)
                raw_request = bytes.fromhex(hex_data)
                pending_request = strip_preambles(raw_request)
                continue

            # Try to match a response line
            rx_match = RX_PATTERN.search(line)
            if rx_match and pending_request is not None:
                hex_data = rx_match.group(1)
                response = bytes.fromhex(hex_data)

                if pending_request not in request_responses:
                    request_responses[pending_request] = []
                request_responses[pending_request].append(response)

                pending_request = None

    return request_responses


class LogResponseProvider:
    """Provides responses from parsed log data with round-robin selection."""

    def __init__(self, request_responses: Dict[bytes, List[bytes]]):
        self._request_responses = request_responses
        self._response_indices: Dict[bytes, int] = {}

    def get_response(self, request: bytes) -> bytes | None:
        """
        Get the next response for a given request.

        Args:
            request: Request frame with preambles stripped

        Returns:
            Response bytes or None if no matching request found
        """
        if request not in self._request_responses:
            return None

        responses = self._request_responses[request]
        index = self._response_indices.get(request, 0)
        response = responses[index]

        # Advance to next response (round-robin)
        self._response_indices[request] = (index + 1) % len(responses)

        return response

    def get_request_count(self) -> int:
        """Return the number of unique requests in the log."""
        return len(self._request_responses)

    def get_total_response_count(self) -> int:
        """Return the total number of responses in the log."""
        return sum(len(responses) for responses in self._request_responses.values())
