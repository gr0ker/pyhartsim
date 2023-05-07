from dataclasses import dataclass
from .payloads import F32, U16, U24, U8, Ascii, PackedAscii


@dataclass
class HartDevice:
    # HART identification
    polling_address: U8 = U8(0)
    long_address: int = 0x2606123456
    is_burst_mode: bool = False
    expanded_device_type: U16 = U16(0x2606)
    device_id: U24 = U24(0x123456)
    message: PackedAscii = PackedAscii(32, "????????????????????????????????")
    long_tag: Ascii = Ascii(32, "                                ")
    # HART status
    device_status: U8 = U8()
    extended_device_status: U8 = U8()
    # HART parameters
    config_change_counter: U16 = U16(0)
    # Analog output
    loop_current_mode: U8 = U8(1)
    loop_current: F32 = F32(4.321)
    percent_of_range: F32 = F32(0.0200625)
    # Dynamic variables
    pv_units: U8 = U8(12)
    pv_value: F32 = F32(1.2345)
    pv_classification: U8 = U8(65)
    sv_units: U8 = U8(32)
    sv_value: F32 = F32(23.4567)
    sv_classification: U8 = U8()
    tv_units: U8 = U8(240)
    tv_value: F32 = F32(345)
    tv_classification: U8 = U8()
    qv_units: U8 = U8(12)
    qv_value: F32 = F32(1.2345)
    qv_classification: U8 = U8()
