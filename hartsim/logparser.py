import re
from functools import reduce
from typing import Dict, List


# Regex patterns for raw hex log format
TX_PATTERN = re.compile(r'Master MAC on \("[^"]+"\) Tx: time [\d.]+ data "([0-9A-Fa-f]+)"')
RX_PATTERN = re.compile(r'RCV_MSG \("[^"]+"\): time [\d.]+ \(ACK\) \d+\+\d+ bytes "([0-9A-Fa-f]+)"')

# Regex for FDI structured text format
# Matches: POL(0) CMD(0) or TYP(0x264A) UID(0x2DC704) CMD(128) DAT(00-01-02)
FDI_FRAME_PATTERN = re.compile(
    r'(?:(?:POL\((?P<PollingAddress>\d+)\))'
    r'|(?:TYP\(0x(?P<ExpandedDeviceType>[A-Fa-f0-9]{4})\) UID\(0x(?P<DeviceId>[A-Fa-f0-9]{6})\)))'
    r'(?: EXP\((?P<ExpansionBytes>[A-Fa-f0-9-]+)\))?'
    r' CMD\((?P<Command>\d+)\)'
    r'(?: DAT\((?P<Data>[A-Fa-f0-9-]+)\))?'
)
FDI_SENDING_PATTERN = re.compile(r'Sending\b', re.IGNORECASE)
FDI_RECEIVED_PATTERN = re.compile(r'Received\b', re.IGNORECASE)

# STX/ACK delimiter values
_STX_SHORT = 0x02
_STX_LONG = 0x82
_ACK_SHORT = 0x06
_ACK_LONG = 0x86
_PRIMARY_MASTER_MASK = 0x80


def strip_preambles(data: bytes) -> bytes:
    """Strip leading 0xFF preamble bytes from frame data."""
    i = 0
    while i < len(data) and data[i] == 0xFF:
        i += 1
    return data[i:]


def _parse_fdi_hex(hex_str: str) -> bytes:
    """Parse dash-separated hex string like '00-50-FE' into bytes."""
    return bytes(int(b, 16) for b in hex_str.split('-'))


def _build_frame(match: re.Match, is_response: bool) -> bytes | None:
    """Build raw HART frame bytes from a FDI regex match."""
    command = int(match.group('Command'))
    data = _parse_fdi_hex(match.group('Data')) if match.group('Data') else b''

    polling_addr_str = match.group('PollingAddress')
    is_long = polling_addr_str is None

    if is_long:
        device_type = int(match.group('ExpandedDeviceType'), 16)
        device_id = int(match.group('DeviceId'), 16)
        delimiter = _ACK_LONG if is_response else _STX_LONG
        # 5 address bytes: first byte has primary master bit for requests
        addr_first = (device_type >> 8) & 0x3F
        if not is_response:
            addr_first |= _PRIMARY_MASTER_MASK
        address_bytes = bytes([
            addr_first,
            device_type & 0xFF,
            (device_id >> 16) & 0xFF,
            (device_id >> 8) & 0xFF,
            device_id & 0xFF,
        ])
    else:
        polling_addr = int(polling_addr_str)
        delimiter = _ACK_SHORT if is_response else _STX_SHORT
        addr_byte = polling_addr & 0x3F
        if not is_response:
            addr_byte |= _PRIMARY_MASTER_MASK
        address_bytes = bytes([addr_byte])

    frame = bytearray()
    frame.append(delimiter)
    frame.extend(address_bytes)
    frame.append(command)
    frame.append(len(data))
    frame.extend(data)
    frame.append(reduce(lambda x, y: x ^ y, frame))
    return bytes(frame)


def _parse_raw_hex_log(file_path: str) -> Dict[bytes, List[bytes]]:
    """Parse raw hex format log file."""
    request_responses: Dict[bytes, List[bytes]] = {}
    pending_request: bytes | None = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            tx_match = TX_PATTERN.search(line)
            if tx_match:
                hex_data = tx_match.group(1)
                raw_request = bytes.fromhex(hex_data)
                pending_request = strip_preambles(raw_request)
                continue

            rx_match = RX_PATTERN.search(line)
            if rx_match and pending_request is not None:
                hex_data = rx_match.group(1)
                response = bytes.fromhex(hex_data)

                if pending_request not in request_responses:
                    request_responses[pending_request] = []
                request_responses[pending_request].append(response)

                pending_request = None

    return request_responses


def _parse_fdi_log(file_path: str) -> Dict[bytes, List[bytes]]:
    """Parse FDI structured text format log file."""
    request_responses: Dict[bytes, List[bytes]] = {}
    pending_request: bytes | None = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if FDI_SENDING_PATTERN.search(line):
                match = FDI_FRAME_PATTERN.search(line)
                if match:
                    pending_request = _build_frame(match, is_response=False)
                continue

            if pending_request is not None and FDI_RECEIVED_PATTERN.search(line):
                match = FDI_FRAME_PATTERN.search(line)
                if match:
                    response = _build_frame(match, is_response=True)
                    if response is not None:
                        if pending_request not in request_responses:
                            request_responses[pending_request] = []
                        request_responses[pending_request].append(response)
                    pending_request = None

    return request_responses


def _detect_format(file_path: str) -> str:
    """Detect log file format by scanning first lines for known patterns."""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if TX_PATTERN.search(line):
                return 'raw'
            if FDI_SENDING_PATTERN.search(line) and FDI_FRAME_PATTERN.search(line):
                return 'fdi'
    return 'raw'


def parse_log_file(file_path: str) -> Dict[bytes, List[bytes]]:
    """
    Parse a HART communication log file and extract request/response pairs.
    Auto-detects log format (raw hex or FDI structured text).

    Args:
        file_path: Path to the log file

    Returns:
        Dictionary mapping request frames (preambles stripped) to lists of response frames
    """
    fmt = _detect_format(file_path)
    if fmt == 'fdi':
        return _parse_fdi_log(file_path)
    return _parse_raw_hex_log(file_path)


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
