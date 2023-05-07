from dataclasses import dataclass
from .payloads import F32, U16, U24, U32, U8, Ascii, PackedAscii, PayloadSequence
from .devices import HartDevice


def handle_request(device: HartDevice, command_number: int, data: bytearray)\
        -> bytearray:
    if command_number == 0:
        payload = Cmd0Reply.create(device)
    elif command_number == 1:
        payload = Cmd1Reply.create(device)
    elif command_number == 2:
        payload = Cmd2Reply.create(device)
    elif command_number == 3:
        payload = Cmd3Reply.create(device)
    elif command_number == 7:
        payload = Cmd7Reply.create(device)
    elif command_number == 8:
        payload = Cmd8Reply.create(device)
    elif command_number == 9:
        request = Cmd9Request()
        request.deserialize(iter(data))
        payload = Cmd9Reply.create(device)
        payload.device_variable_code_1.set_value(
            request.device_variable_code_1.get_value())
        if request.device_variable_code_2.is_skipped():
            payload.device_variable_code_2.skip()
            payload.device_variable_classification_2.skip()
            payload.device_variable_units_2.skip()
            payload.device_variable_value_2.skip()
            payload.device_variable_status_2.skip()
        else:
            payload.device_variable_code_2.set_value(
                request.device_variable_code_2.get_value())
            payload.device_variable_code_2.include()
            payload.device_variable_classification_2.include()
            payload.device_variable_units_2.include()
            payload.device_variable_value_2.include()
            payload.device_variable_status_2.include()
        if request.device_variable_code_3.is_skipped():
            payload.device_variable_code_3.skip()
            payload.device_variable_classification_3.skip()
            payload.device_variable_units_3.skip()
            payload.device_variable_value_3.skip()
            payload.device_variable_status_3.skip()
        else:
            payload.device_variable_code_3.set_value(
                request.device_variable_code_3.get_value())
            payload.device_variable_code_3.include()
            payload.device_variable_classification_3.include()
            payload.device_variable_units_3.include()
            payload.device_variable_value_3.include()
            payload.device_variable_status_3.include()
        if request.device_variable_code_4.is_skipped():
            payload.device_variable_code_4.skip()
            payload.device_variable_classification_4.skip()
            payload.device_variable_units_4.skip()
            payload.device_variable_value_4.skip()
            payload.device_variable_status_4.skip()
        else:
            payload.device_variable_code_4.set_value(
                request.device_variable_code_4.get_value())
            payload.device_variable_code_4.include()
            payload.device_variable_classification_4.include()
            payload.device_variable_units_4.include()
            payload.device_variable_value_4.include()
            payload.device_variable_status_4.include()
        if request.device_variable_code_5.is_skipped():
            payload.device_variable_code_5.skip()
            payload.device_variable_classification_5.skip()
            payload.device_variable_units_5.skip()
            payload.device_variable_value_5.skip()
            payload.device_variable_status_5.skip()
        else:
            payload.device_variable_code_5.set_value(
                request.device_variable_code_5.get_value())
            payload.device_variable_code_5.include()
            payload.device_variable_classification_5.include()
            payload.device_variable_units_5.include()
            payload.device_variable_value_5.include()
            payload.device_variable_status_5.include()
        if request.device_variable_code_6.is_skipped():
            payload.device_variable_code_6.skip()
            payload.device_variable_classification_6.skip()
            payload.device_variable_units_6.skip()
            payload.device_variable_value_6.skip()
            payload.device_variable_status_6.skip()
        else:
            payload.device_variable_code_6.set_value(
                request.device_variable_code_6.get_value())
            payload.device_variable_code_6.include()
            payload.device_variable_classification_6.include()
            payload.device_variable_units_6.include()
            payload.device_variable_value_6.include()
            payload.device_variable_status_6.include()
        if request.device_variable_code_7.is_skipped():
            payload.device_variable_code_7.skip()
            payload.device_variable_classification_7.skip()
            payload.device_variable_units_7.skip()
            payload.device_variable_value_7.skip()
            payload.device_variable_status_7.skip()
        else:
            payload.device_variable_code_7.set_value(
                request.device_variable_code_7.get_value())
            payload.device_variable_code_7.include()
            payload.device_variable_classification_7.include()
            payload.device_variable_units_7.include()
            payload.device_variable_value_7.include()
            payload.device_variable_status_7.include()
        if request.device_variable_code_8.is_skipped():
            payload.device_variable_code_8.skip()
            payload.device_variable_classification_8.skip()
            payload.device_variable_units_8.skip()
            payload.device_variable_value_8.skip()
            payload.device_variable_status_8.skip()
        else:
            payload.device_variable_code_8.set_value(
                request.device_variable_code_8.get_value())
            payload.device_variable_code_8.include()
            payload.device_variable_classification_8.include()
            payload.device_variable_units_8.include()
            payload.device_variable_value_8.include()
            payload.device_variable_status_8.include()
    elif command_number == 12:
        payload = Cmd12Reply.create(device)
    elif command_number == 20:
        payload = Cmd20Reply.create(device)
    else:
        payload = ErrorReply.create(device)
        payload.response_code = U8(64)

    return list(payload)


@dataclass
class Cmd0Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    expansion_code: U8 = U8(254)
    expanded_device_type: U16 = U16()
    request_preambles: U8 = U8(5)
    universal_revision: U8 = U8(7)
    device_revision: U8 = U8(10)
    software_revision: U8 = U8(3)
    hardware_revision_signaling_code: U8 = U8(0x64)
    flags: U8 = U8()
    device_id: U24 = U24()
    response_preambles: U8 = U8(5)
    max_device_variables: U8 = U8(1)
    config_change_counter: U16 = U16()
    extended_device_status: U8 = U8()
    manufacturer_code: U16 = U16(0x0026)
    private_label_distributor: U16 = U16(0x0026)
    device_profile: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice):
        return Cmd0Reply(
            device_status=device.device_status,
            expanded_device_type=device.expanded_device_type,
            device_id=device.device_id,
            config_change_counter=device.config_change_counter,
            extended_device_status=device.extended_device_status)


@dataclass
class Cmd1Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    pv_units: U8 = U8()
    pv_value: F32 = F32()

    @classmethod
    def create(cls, device: HartDevice):
        return Cmd1Reply(
            device_status=device.device_status,
            pv_units=device.pv_units,
            pv_value=device.pv_value)


@dataclass
class Cmd2Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    loop_current: U8 = U8()
    percent_of_range: F32 = F32()

    @classmethod
    def create(cls, device: HartDevice):
        return Cmd2Reply(
            device_status=device.device_status,
            loop_current=device.loop_current,
            percent_of_range=device.percent_of_range)


@dataclass
class Cmd3Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    loop_current: F32 = F32()
    pv_units: U8 = U8()
    pv_value: F32 = F32()
    sv_units: U8 = U8()
    sv_value: F32 = F32()
    tv_units: U8 = U8()
    tv_value: F32 = F32()
    qv_units: U8 = U8()
    qv_value: F32 = F32()

    @classmethod
    def create(cls, device: HartDevice):
        return Cmd3Reply(
            device_status=device.device_status,
            pv_units=device.pv_units,
            pv_value=device.pv_value,
            sv_units=device.sv_units,
            sv_value=device.sv_value,
            tv_units=device.tv_units,
            tv_value=device.tv_value,
            qv_units=device.qv_units,
            qv_value=device.qv_value)


@dataclass
class Cmd7Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    polling_address: U8 = U8()
    loop_current_mode: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice):
        return Cmd7Reply(
            device_status=device.device_status,
            polling_address=device.polling_address,
            loop_current_mode=device.loop_current_mode)


@dataclass
class Cmd8Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    pv_classification: U8 = U8()
    sv_classification: U8 = U8()
    tv_classification: U8 = U8()
    qv_classification: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice):
        return Cmd8Reply(
            device_status=device.device_status,
            pv_classification=device.pv_classification,
            sv_classification=device.sv_classification,
            tv_classification=device.tv_classification,
            qv_classification=device.qv_classification)


@dataclass
class Cmd9Request (PayloadSequence):
    device_variable_code_1: U8 = U8()
    device_variable_code_2: U8 = U8(is_optional=True)
    device_variable_code_3: U8 = U8(is_optional=True)
    device_variable_code_4: U8 = U8(is_optional=True)
    device_variable_code_5: U8 = U8(is_optional=True)
    device_variable_code_6: U8 = U8(is_optional=True)
    device_variable_code_7: U8 = U8(is_optional=True)
    device_variable_code_8: U8 = U8(is_optional=True)


@dataclass
class Cmd9Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    extended_device_status: U8 = U8()
    device_variable_code_1: U8 = U8()
    device_variable_classification_1: U8 = U8()
    device_variable_units_1: U8 = U8()
    device_variable_value_1: F32 = F32()
    device_variable_status_1: U8 = U8()
    device_variable_code_2: U8 = U8(is_optional=True)
    device_variable_classification_2: U8 = U8(is_optional=True)
    device_variable_units_2: U8 = U8(is_optional=True)
    device_variable_value_2: F32 = F32(is_optional=True)
    device_variable_status_2: U8 = U8(is_optional=True)
    device_variable_code_3: U8 = U8(is_optional=True)
    device_variable_classification_3: U8 = U8(is_optional=True)
    device_variable_units_3: U8 = U8(is_optional=True)
    device_variable_value_3: F32 = F32(is_optional=True)
    device_variable_status_3: U8 = U8(is_optional=True)
    device_variable_code_4: U8 = U8(is_optional=True)
    device_variable_classification_4: U8 = U8(is_optional=True)
    device_variable_units_4: U8 = U8(is_optional=True)
    device_variable_value_4: F32 = F32(is_optional=True)
    device_variable_status_4: U8 = U8(is_optional=True)
    device_variable_code_5: U8 = U8(is_optional=True)
    device_variable_classification_5: U8 = U8(is_optional=True)
    device_variable_units_5: U8 = U8(is_optional=True)
    device_variable_value_5: F32 = F32(is_optional=True)
    device_variable_status_5: U8 = U8(is_optional=True)
    device_variable_code_6: U8 = U8(is_optional=True)
    device_variable_classification_6: U8 = U8(is_optional=True)
    device_variable_units_6: U8 = U8(is_optional=True)
    device_variable_value_6: F32 = F32(is_optional=True)
    device_variable_status_6: U8 = U8(is_optional=True)
    device_variable_code_7: U8 = U8(is_optional=True)
    device_variable_classification_7: U8 = U8(is_optional=True)
    device_variable_units_7: U8 = U8(is_optional=True)
    device_variable_value_7: F32 = F32(is_optional=True)
    device_variable_status_7: U8 = U8(is_optional=True)
    device_variable_code_8: U8 = U8(is_optional=True)
    device_variable_classification_8: U8 = U8(is_optional=True)
    device_variable_units_8: U8 = U8(is_optional=True)
    device_variable_value_8: F32 = F32(is_optional=True)
    device_variable_status_8: U8 = U8(is_optional=True)
    timestamp: U32 = U32()

    @classmethod
    def create(cls, device: HartDevice):
        return Cmd9Reply(
            device_status=device.device_status,
            extended_device_status=device.extended_device_status)


@dataclass
class Cmd12Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    message: PackedAscii = PackedAscii(32)

    @classmethod
    def create(cls, device: HartDevice):
        return Cmd12Reply(
            device_status=device.device_status,
            message=device.message)


@dataclass
class Cmd20Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    long_tag: Ascii = Ascii(32)

    @classmethod
    def create(cls, device: HartDevice):
        return Cmd20Reply(
            device_status=device.device_status,
            long_tag=device.long_tag)


@dataclass
class ErrorReply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()

    @classmethod
    def create(device: HartDevice, response_code: U8):
        return ErrorReply(
            device_status=device.device_status,
            response_code=response_code)
