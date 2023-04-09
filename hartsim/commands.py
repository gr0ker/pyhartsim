from dataclasses import dataclass
from .payloads import F32, U16, U24, U8, Ascii, PackedAscii, PayloadSequence

polling_address = U8(0)
long_address = bytearray([0x26, 0x06, 0x12, 0x34, 0x56])
is_burst_mode = False

expanded_device_type = U16(0x2606)
device_id: U24 = U24(0x123456)
device_status = U8()
extended_device_status = U8()
config_change_counter = U16(0)

loop_current_mode = U8(1)

pv_units = U8(12)
pv_value = F32(1.2345)
pv_classification = U8(65)

sv_units = U8(32)
sv_value = F32(23.4567)
sv_classification = U8()

tv_units = U8(240)
tv_value = F32(345)
tv_classification = U8()

qv_units = U8(12)
qv_value = F32(1.2345)
qv_classification = U8()

loop_current = F32(4.321)
percent_of_range = F32(0.0200625)

message = PackedAscii(32, "THIS IS A MESSAGE")

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
class Cmd2Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    loop_current: U8 = loop_current
    percent_of_range: F32 = percent_of_range


@dataclass
class Cmd3Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    loop_current: U8 = loop_current
    pv_units: U8 = pv_units
    pv_value: F32 = pv_value
    sv_units: U8 = sv_units
    sv_value: F32 = sv_value
    tv_units: U8 = tv_units
    tv_value: F32 = tv_value
    qv_units: U8 = qv_units
    qv_value: F32 = qv_value


@dataclass
class Cmd7Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    polling_address: U8 = polling_address
    loop_current_mode: U8 = loop_current_mode


@dataclass
class Cmd8Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    pv_classification: U8 = pv_classification
    sv_classification: F32 = sv_classification
    tv_classification: U8 = tv_classification
    qv_classification: F32 = qv_classification


@dataclass
class Cmd12Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    message: PackedAscii = message


@dataclass
class Cmd20Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
    long_tag: Ascii = long_tag


@dataclass
class ErrorReply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = device_status
