from dataclasses import dataclass
from .payloads import F32, U16, U24, U8, Ascii, PayloadSequence

short_address = 0
long_address = bytearray([0x26, 0x06, 0x12, 0x34, 0x56])
is_burst_mode = False

expanded_device_type = U16(0x2606)
device_id: U24 = U24(0x123456)
device_status = U8()
extended_device_status = U8()
config_change_counter = U16(0)

pv_units = U8(12)
pv_value = F32(1.2345)

long_tag = Ascii(32, "This is a HART device simulator")


@dataclass
class Cmd0Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    expansion_code: U8 = U8(254)
    expanded_device_type: U16 = expanded_device_type
    request_preambles: U8 = U8(5)
    universal_revision: U8 = U8(7)
    device_revision: U8 = U8(10)
    software_revision: U8 = U8(3)
    hardware_revision_signaling_code: U8 = U8(0x64)
    flags: U8 = U8()
    device_id: U24 = device_id
    response_preambles: U8 = U8(5)
    max_device_variables: U8 = U8(1)
    config_change_counter: U16 = config_change_counter
    extended_device_status: U8 = extended_device_status
    manufacturer_code: U16 = U16(0x0026)
    private_label_distributor: U16 = U16(0x0026)
    device_profile: U8 = U8()


@dataclass
class Cmd1Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    pv_units: U8 = pv_units
    pv_value: F32 = pv_value


@dataclass
class Cmd20Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    long_tag: U8 = long_tag


@dataclass
class ErrorReply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
