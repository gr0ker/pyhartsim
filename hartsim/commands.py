from dataclasses import dataclass
import random
from .payloads import F32, U16, U24, U32, U8, Ascii, GreedyU8Array, PackedAscii
from .payloads import PayloadSequence
from .devices import HartDevice


def handle_request(device: HartDevice, command_number: int, data: bytearray)\
        -> bytearray:
    is_extended_command = command_number == 31
    if is_extended_command:
        request = Cmd31Request()
        request.deserialize(iter(data))
        command_number = request.extended_command_number
        data = request.request_data

    if command_number == 0:
        # TODO move logic to HartDevice class
        if device.universal_revision.get_value() == 5:
            payload = Cmd0Hart5Reply.create(device)
        else:
            payload = Cmd0Hart7Reply.create(device)
    elif command_number == 1:
        payload = Cmd1Reply.create(device)
    elif command_number == 2:
        payload = Cmd2Reply.create(device)
    elif command_number == 3:
        payload = Cmd3Reply.create(device)
    elif command_number == 7 and device.universal_revision.get_value() >= 6:
        payload = Cmd7Reply.create(device)
    elif command_number == 8 and device.universal_revision.get_value() >= 6:
        payload = Cmd8Reply.create(device)
    elif command_number == 9 and device.universal_revision.get_value() >= 6:
        request = Cmd9Request()
        request.deserialize(iter(data))
        payload = Cmd9Reply.create(device, request)
    elif command_number == 12:
        payload = Cmd12Reply.create(device)
    elif command_number == 13:
        payload = Cmd13Reply.create(device)
    elif command_number == 15:
        payload = Cmd15Reply.create(device)
    elif command_number == 20 and device.universal_revision.get_value() >= 6:
        payload = Cmd20Reply.create(device)
    elif command_number == 48:
        payload = Cmd48Reply.create(device)
    elif command_number == 76:
        payload = Cmd76Reply.create(device)
    elif command_number == 90:
        payload = Cmd90Reply.create(device)
    elif command_number == 105:
        payload = Cmd105Reply.create(device)
    elif command_number == 128:
        payload = Cmd128Reply.create(device)
    elif command_number == 133:
        payload = Cmd133Reply.create(device)
    elif command_number == 148:
        payload = Cmd148Reply.create(device)
    elif command_number == 160:
        payload = Cmd160Reply.create(device)
    elif command_number == 161:
        payload = Cmd161Reply.create(device)
    elif command_number == 162:
        payload = Cmd162Reply.create(device)
    elif command_number == 216:
        payload = Cmd216Reply.create(device)
    elif command_number == 217:
        payload = Cmd217Reply.create(device)
    elif command_number == 218:
        payload = Cmd218Reply.create(device)
    elif command_number == 220:
        payload = Cmd220Reply.create(device)
    elif command_number == 222:
        payload = Cmd222Reply.create(device)
    else:
        payload = ErrorReply.create(device, U8(64))

    if is_extended_command:
        payload = Cmd31Reply.create(
            device,
            payload.response_code,
            command_number,
            # skip Response Code and Device Status
            GreedyU8Array(bytearray(payload)[2:]))
        command_number = 31

    return list(payload)


@dataclass
class Cmd0Hart5Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    expansion_code: U8 = U8(254)
    expanded_device_type: U16 = U16()
    request_preambles: U8 = U8(5)
    universal_revision: U8 = U8(5)
    device_revision: U8 = U8(11)
    software_revision: U8 = U8(3)
    hardware_revision_signaling_code: U8 = U8(0x64)
    flags: U8 = U8()
    device_id: U24 = U24()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status,
            expanded_device_type=device.expanded_device_type,
            device_id=device.device_id)


@dataclass
class Cmd0Hart7Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    expansion_code: U8 = U8(254)
    expanded_device_type: U16 = U16()
    request_preambles: U8 = U8(5)
    universal_revision: U8 = U8(7)
    device_revision: U8 = U8(7)
    software_revision: U8 = U8(3)
    hardware_revision_signaling_code: U8 = U8(0x64)
    flags: U8 = U8()
    device_id: U24 = U24()
    response_preambles: U8 = U8(5)
    max_device_variables: U8 = U8(1)
    config_change_counter: U16 = U16()
    extended_device_status: U8 = U8()
    manufacturer_code: U16 = U16(0x0099)
    private_label_distributor: U16 = U16(0x0099)
    device_profile: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
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
        return cls(
            device_status=device.device_status,
            pv_units=device.device_variables[device.dynamic_variables[0]].units,
            pv_value=device.device_variables[device.dynamic_variables[0]].value,)


@dataclass
class Cmd2Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    loop_current: U8 = U8()
    percent_of_range: F32 = F32()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
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
        return cls(
            device_status=device.device_status,
            loop_current=device.loop_current,
            pv_units=device.device_variables[device.dynamic_variables[0]].units,
            pv_value=device.device_variables[device.dynamic_variables[0]].value,
            sv_units=device.device_variables[device.dynamic_variables[1]].units,
            sv_value=device.device_variables[device.dynamic_variables[1]].value,
            tv_units=device.device_variables[device.dynamic_variables[2]].units,
            tv_value=device.device_variables[device.dynamic_variables[2]].value,
            qv_units=device.device_variables[device.dynamic_variables[3]].units,
            qv_value=device.device_variables[device.dynamic_variables[3]].value)


@dataclass
class Cmd7Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    polling_address: U8 = U8()
    loop_current_mode: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
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
        return cls(
            device_status=device.device_status,
            pv_classification=device.device_variables[device.dynamic_variables[0]].classification,
            sv_classification=device.device_variables[device.dynamic_variables[1]].classification,
            tv_classification=device.device_variables[device.dynamic_variables[2]].classification,
            qv_classification=device.device_variables[device.dynamic_variables[3]].classification)


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
    def create(cls, device: HartDevice, request: Cmd9Request):
        payload = cls(
            device_status=device.device_status,
            extended_device_status=device.extended_device_status)

        payload.device_variable_code_1.set_value(
            request.device_variable_code_1.get_value())

        payload.device_variable_classification_1.set_value(
            device.device_variables[request.device_variable_code_1.get_value()].classification.get_value())
        payload.device_variable_units_1.set_value(
            device.device_variables[request.device_variable_code_1.get_value()].units.get_value())
        payload.device_variable_value_1.set_value(
            device.device_variables[request.device_variable_code_1.get_value()].value.get_value())
        payload.device_variable_status_1.set_value(
            device.device_variables[request.device_variable_code_1.get_value()].status.get_value())

        new_units = device.device_variables[request.device_variable_code_1.get_value(
        )].alternate_units.get_value()
        device.device_variables[request.device_variable_code_1.get_value()].alternate_units.set_value(
            device.device_variables[request.device_variable_code_1.get_value()].units.get_value())
        device.device_variables[request.device_variable_code_1.get_value(
        )].units.set_value(new_units)

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
            payload.device_variable_classification_2.set_value(
                device.device_variables[request.device_variable_code_2.get_value()].classification.get_value())
            payload.device_variable_units_2.include()
            payload.device_variable_units_2.set_value(
                device.device_variables[request.device_variable_code_2.get_value()].units.get_value())
            payload.device_variable_value_2.include()
            payload.device_variable_value_2.set_value(
                device.device_variables[request.device_variable_code_2.get_value()].value.get_value())
            payload.device_variable_status_2.include()
            payload.device_variable_status_2.set_value(
                device.device_variables[request.device_variable_code_2.get_value()].status.get_value())

            new_units = device.device_variables[request.device_variable_code_2.get_value(
            )].alternate_units.get_value()
            device.device_variables[request.device_variable_code_2.get_value()].alternate_units.set_value(
                device.device_variables[request.device_variable_code_2.get_value()].units.get_value())
            device.device_variables[request.device_variable_code_2.get_value(
            )].units.set_value(new_units)
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
            payload.device_variable_classification_3.set_value(
                device.device_variables[request.device_variable_code_3.get_value()].classification.get_value())
            payload.device_variable_units_3.include()
            payload.device_variable_units_3.set_value(
                device.device_variables[request.device_variable_code_3.get_value()].units.get_value())
            payload.device_variable_value_3.include()
            payload.device_variable_value_3.set_value(
                device.device_variables[request.device_variable_code_3.get_value()].value.get_value())
            payload.device_variable_status_3.include()
            payload.device_variable_status_3.set_value(
                device.device_variables[request.device_variable_code_3.get_value()].status.get_value())

            new_units = device.device_variables[request.device_variable_code_3.get_value(
            )].alternate_units.get_value()
            device.device_variables[request.device_variable_code_3.get_value()].alternate_units.set_value(
                device.device_variables[request.device_variable_code_3.get_value()].units.get_value())
            device.device_variables[request.device_variable_code_3.get_value(
            )].units.set_value(new_units)
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
            payload.device_variable_classification_4.set_value(
                device.device_variables[request.device_variable_code_4.get_value()].classification.get_value())
            payload.device_variable_units_4.include()
            payload.device_variable_units_4.set_value(
                device.device_variables[request.device_variable_code_4.get_value()].units.get_value())
            payload.device_variable_value_4.include()
            payload.device_variable_value_4.set_value(
                device.device_variables[request.device_variable_code_4.get_value()].value.get_value())
            payload.device_variable_status_4.include()
            payload.device_variable_status_4.set_value(
                device.device_variables[request.device_variable_code_4.get_value()].status.get_value())

            new_units = device.device_variables[request.device_variable_code_4.get_value(
            )].alternate_units.get_value()
            device.device_variables[request.device_variable_code_4.get_value()].alternate_units.set_value(
                device.device_variables[request.device_variable_code_4.get_value()].units.get_value())
            device.device_variables[request.device_variable_code_4.get_value(
            )].units.set_value(new_units)
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
            payload.device_variable_classification_5.set_value(
                device.device_variables[request.device_variable_code_5.get_value()].classification.get_value())
            payload.device_variable_units_5.include()
            payload.device_variable_units_5.set_value(
                device.device_variables[request.device_variable_code_5.get_value()].units.get_value())
            payload.device_variable_value_5.include()
            payload.device_variable_value_5.set_value(
                device.device_variables[request.device_variable_code_5.get_value()].value.get_value())
            payload.device_variable_status_5.include()
            payload.device_variable_status_5.set_value(
                device.device_variables[request.device_variable_code_5.get_value()].status.get_value())

            new_units = device.device_variables[request.device_variable_code_5.get_value(
            )].alternate_units.get_value()
            device.device_variables[request.device_variable_code_5.get_value()].alternate_units.set_value(
                device.device_variables[request.device_variable_code_5.get_value()].units.get_value())
            device.device_variables[request.device_variable_code_5.get_value(
            )].units.set_value(new_units)
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
            payload.device_variable_classification_6.set_value(
                device.device_variables[request.device_variable_code_6.get_value()].classification.get_value())
            payload.device_variable_units_6.include()
            payload.device_variable_units_6.set_value(
                device.device_variables[request.device_variable_code_6.get_value()].units.get_value())
            payload.device_variable_value_6.include()
            payload.device_variable_value_6.set_value(
                device.device_variables[request.device_variable_code_6.get_value()].value.get_value())
            payload.device_variable_status_6.include()
            payload.device_variable_status_6.set_value(
                device.device_variables[request.device_variable_code_6.get_value()].status.get_value())

            new_units = device.device_variables[request.device_variable_code_6.get_value(
            )].alternate_units.get_value()
            device.device_variables[request.device_variable_code_6.get_value()].alternate_units.set_value(
                device.device_variables[request.device_variable_code_6.get_value()].units.get_value())
            device.device_variables[request.device_variable_code_6.get_value(
            )].units.set_value(new_units)
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
            payload.device_variable_classification_7.set_value(
                device.device_variables[request.device_variable_code_7.get_value()].classification.get_value())
            payload.device_variable_units_7.include()
            payload.device_variable_units_7.set_value(
                device.device_variables[request.device_variable_code_7.get_value()].units.get_value())
            payload.device_variable_value_7.include()
            payload.device_variable_value_7.set_value(
                device.device_variables[request.device_variable_code_7.get_value()].value.get_value())
            payload.device_variable_status_7.include()
            payload.device_variable_status_7.set_value(
                device.device_variables[request.device_variable_code_7.get_value()].status.get_value())

            new_units = device.device_variables[request.device_variable_code_7.get_value(
            )].alternate_units.get_value()
            device.device_variables[request.device_variable_code_7.get_value()].alternate_units.set_value(
                device.device_variables[request.device_variable_code_7.get_value()].units.get_value())
            device.device_variables[request.device_variable_code_7.get_value(
            )].units.set_value(new_units)
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
            payload.device_variable_classification_8.set_value(
                device.device_variables[request.device_variable_code_8.get_value()].classification.get_value())
            payload.device_variable_units_8.include()
            payload.device_variable_units_8.set_value(
                device.device_variables[request.device_variable_code_8.get_value()].units.get_value())
            payload.device_variable_value_8.include()
            payload.device_variable_value_8.set_value(
                device.device_variables[request.device_variable_code_8.get_value()].value.get_value())
            payload.device_variable_status_8.include()
            payload.device_variable_status_8.set_value(
                device.device_variables[request.device_variable_code_8.get_value()].status.get_value())

            new_units = device.device_variables[request.device_variable_code_8.get_value(
            )].alternate_units.get_value()
            device.device_variables[request.device_variable_code_8.get_value()].alternate_units.set_value(
                device.device_variables[request.device_variable_code_8.get_value()].units.get_value())
            device.device_variables[request.device_variable_code_8.get_value(
            )].units.set_value(new_units)

        return payload


@dataclass
class Cmd12Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    hart_message: PackedAscii = PackedAscii(32)

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status,
            hart_message=device.hart_message)


@dataclass
class Cmd13Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    hart_tag: PackedAscii = PackedAscii(8)
    hart_descriptor: PackedAscii = PackedAscii(16)
    hart_date: U24 = U24()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status,
            hart_tag=device.hart_tag,
            hart_descriptor=device.hart_descriptor,
            hart_date=device.hart_date)


@dataclass
class Cmd15Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: U32 = U32()
    reserved_1: U32 = U32()
    reserved_2: U32 = U32()
    reserved_3: U32 = U32()
    reserved_4: U24 = U24()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd20Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    long_tag: Ascii = Ascii(32)

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status,
            long_tag=device.hart_long_tag)


@dataclass
class Cmd48Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    device_specific_status_0: U8 = U8()
    device_specific_status_1: U8 = U8()
    device_specific_status_2: U8 = U8()
    device_specific_status_3: U8 = U8(0x10)
    device_specific_status_4: U8 = U8()
    device_specific_status_5: U8 = U8()
    extended_fld_device_status: U8 = U8()
    reserved_0: U8 = U8()
    reserved_1: U8 = U8()
    reserved_2: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice):
        payload = cls(
            device_status=device.device_status)

        payload.device_specific_status_0.set_value(
            device.device_specific_status_0.get_value())

        new_device_specific_status_0 = device.alternate_device_specific_status_0.get_value()
        device.alternate_device_specific_status_0.set_value(
            device.device_specific_status_0.get_value())
        device.device_specific_status_0.set_value(new_device_specific_status_0)

        return payload


@dataclass
class Cmd76Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    lock_status: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd90Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    year: U8 = U8()
    current_time: U32 = U32()
    day_clock_last_set: U8 = U8()
    month_clock_last_set: U8 = U8()
    year_clock_last_set: U8 = U8()
    time_clock_last_set: U32 = U32()
    rtc_flags: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd105Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    burst_mode_control_code: U8 = U8()
    burst_command_number_expansion_flag: U8 = U8()
    device_variable_code_slot_0: U8 = U8()
    device_variable_code_slot_1: U8 = U8()
    device_variable_code_slot_2: U8 = U8()
    device_variable_code_slot_3: U8 = U8()
    device_variable_code_slot_4: U8 = U8()
    device_variable_code_slot_5: U8 = U8()
    device_variable_code_slot_6: U8 = U8()
    device_variable_code_slot_7: U8 = U8()
    burst_message: U8 = U8()
    number_of_burst_messages: U8 = U8()
    extended_command_number: U16 = U16()
    update_period: U32 = U32()
    maximum_update_period: U32 = U32()
    burst_trigger_mode: U8 = U8()
    classification: U8 = U8()
    units_code: U8 = U8()
    trigger_level: F32 = U32()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd128Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: Ascii = Ascii(31)

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd133Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: U24 = U24()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd148Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: PackedAscii = PackedAscii(32)

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd160Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: PackedAscii = PackedAscii(32)

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd161Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: Ascii = Ascii(3)
    tank_type: U8 = U8(5)  # custom
    reserved_1: Ascii = Ascii(12)

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd162Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: Ascii = Ascii(83)

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd216Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: U32 = U32()
    reserved_1: U32 = U32()
    reserved_2: U32 = U32()
    reserved_3: U32 = U32()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd217Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: U32 = U32()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd218Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: U32 = U32()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd220Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: U32 = U32()
    reserved_1: U32 = U32()
    reserved_2: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class Cmd222Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    reserved_0: U32 = U32()

    @classmethod
    def create(cls, device: HartDevice):
        return cls(
            device_status=device.device_status)


@dataclass
class ErrorReply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()

    @classmethod
    def create(cls, device: HartDevice, response_code: U8):
        return cls(
            device_status=device.device_status,
            response_code=response_code)


@dataclass
class Cmd31Request (PayloadSequence):
    extended_command_number: U16 = U16()
    request_data: GreedyU8Array = GreedyU8Array()


@dataclass
class Cmd31Reply (PayloadSequence):
    response_code: U8 = U8()
    device_status: U8 = U8()
    extended_command_number: U16 = U16()
    response_data: GreedyU8Array = GreedyU8Array()

    @classmethod
    def create(cls,
               device: HartDevice,
               response_code: U8,
               extended_command_number: U16,
               response_data: GreedyU8Array):
        return cls(
            device_status=device.device_status,
            response_code=response_code,
            extended_command_number=extended_command_number,
            response_data=response_data)
