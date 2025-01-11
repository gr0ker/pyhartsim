from dataclasses import dataclass
from .payloads import F32, U16, U24, U8, Ascii, PackedAscii


@dataclass
class DeviceVariable:
    units: U8 = U8()
    alternate_units: U8 = U8()
    value: F32 = F32()
    classification: U8 = U8()
    status: U8 = U8()


@dataclass
class HartDevice:
    device_variables: dict[int, DeviceVariable]
    dynamic_variables: dict[int, int]
    # HART identification
    polling_address: U8 = U8(0)
    long_address: int = 0x2606123456
    is_burst_mode: bool = False
    expanded_device_type: U16 = U16(0x2606)
    device_id: U24 = U24(0x123456)
    hart_tag: PackedAscii = PackedAscii(8, "????????")
    hart_descriptor: PackedAscii = PackedAscii(16, "????????????????")
    hart_date: U24 = U24(0x010100)
    hart_message: PackedAscii = PackedAscii(
        32, "????????????????????????????????")
    hart_long_tag: Ascii = Ascii(32, "                                ")
    universal_revision: U8 = U8(7)
    # HART status
    device_status: U8 = U8()
    extended_device_status: U8 = U8()
    # HART parameters
    config_change_counter: U16 = U16(0)
    # Analog output
    loop_current_mode: U8 = U8(1)
    loop_current: F32 = F32(4.321)
    percent_of_range: F32 = F32(0.0200625)
    device_specific_status_0: U8 = U8(0x02)
    alternate_device_specific_status_0: U8 = U8()
    display_parameters: U16 = U16(0xAAAA)
    alarm_saturation_setting: U8 = U8(1)
    high_alarm_level: F32 = F32(23.0)
    low_alarm_level: F32 = F32(3.4)
    high_saturation_level: F32 = F32(22.8)
    low_saturation_level: F32 = F32(3.9)
    # Device Variables
    # pressure: DeviceVariable = DeviceVariable(12, 1.2345, 65, 192)
    # temperature: DeviceVariable = DeviceVariable(32, 23.456, 0, 192)
    # flow: DeviceVariable = DeviceVariable(241, 345.67, 0, 192)
    # totalizer: DeviceVariable = DeviceVariable(241, 4567.8, 0, 192)
    # level: DeviceVariable = DeviceVariable(45, 5.6789, 0, 192)
    # volume: DeviceVariable = DeviceVariable(41, 67.890, 0, 192)
    # dict[int, DeviceVariable]
    # {
    #     0: pressure,
    #     1: temperature,
    #     2: flow,
    #     3: totalizer,
    #     4: level,
    #     5: volume,
    # }
    # Dynamic variables
    # dict[int, int]
    # {
    #     0: 0,
    #     1: 1,
    #     2: 2,
    #     3: 3,
    # }
