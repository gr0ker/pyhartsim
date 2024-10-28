import pytest
import unittest

from unittest.mock import patch, mock_open
from pydantic import ValidationError

from hartsim import U8, F32, U24, U16, HartFrame, FrameType
from hartsim.devices import DeviceSpec, Device, InvalidDeviceSpecError, CommandDispatcher


class TestDevices(unittest.TestCase):

    def test_device_spec_load_empty(self):
        data = {
            'variables': [],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                target = DeviceSpec.load('dummy_path')
                self.assertEqual(0, len(target.variables))
                self.assertEqual(0, len(target.commands))

    def test_device_spec_load(self):
        data = {
            'variables': [
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': [
                {'number': 123, 'request': [], 'reply': [{ 'name': 'some_variable' }]},
                {'number': 4567, 'request': [{'name': 'some_variable'}], 'reply': [{'name': 'some_variable'}, {'name': 'another_variable'}]}
            ]
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                target = DeviceSpec.load('dummy_path')
                self.assertEqual(2, len(target.variables))

                self.assertEqual('some_variable', target.variables[0].name)
                self.assertEqual('U8', target.variables[0].type)
                self.assertEqual(None, target.variables[0].value)

                self.assertEqual('another_variable', target.variables[1].name)
                self.assertEqual('F32', target.variables[1].type)
                self.assertEqual(1.234, target.variables[1].value)

                self.assertEqual(2, len(target.commands))

                self.assertEqual(123, target.commands[0].number)
                self.assertEqual(0, len(target.commands[0].request))
                self.assertEqual(1, len(target.commands[0].reply))
                self.assertEqual('some_variable', target.commands[0].reply[0].name)

                self.assertEqual(4567, target.commands[1].number)
                self.assertEqual(1, len(target.commands[1].request))
                self.assertEqual('some_variable', target.commands[1].request[0].name)
                self.assertEqual(2, len(target.commands[1].reply))
                self.assertEqual('some_variable', target.commands[1].reply[0].name)
                self.assertEqual('another_variable', target.commands[1].reply[1].name)

    def test_device_spec_variables_load(self):
        data = {
            'variables': [
                {'name': 'some_variable', 'type': 'U8'}
            ],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                DeviceSpec.load('dummy_path')

    def test_device_spec_variables_fail_on_missing_type(self):
        data = {
            'variables': [
                {'name': 'some_variable'}
            ],
            'commands': []
        }

        with pytest.raises(ValidationError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    DeviceSpec.load('dummy_path')

        self.assertIsNotNone(exception_info.value)

    def test_device_spec_variables_fail_on_missing_name(self):
        data = {
            'variables': [
                {'type': 'U8'}
            ],
            'commands': []
        }

        with pytest.raises(ValidationError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    DeviceSpec.load('dummy_path')

        self.assertIsNotNone(exception_info.value)

    def test_device_spec_commands_load(self):
        data = {
            'variables': [
                {'name': 'some_variable', 'type': 'U8'}
            ],
            'commands': [
                {'number': 123, 'request': [], 'reply': [{'name': 'some_variable'}]}
            ]
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                DeviceSpec.load('dummy_path')

    def test_device_spec_commands_fail_on_missing_number(self):
        data = {
            'variables': [
                {'type': 'U8'}
            ],
            'commands': [
                {'request': [], 'reply': [{'name': 'some_variable'}]}
            ]
        }

        with pytest.raises(ValidationError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    DeviceSpec.load('dummy_path')

        self.assertIsNotNone(exception_info.value)

    def test_device_spec_commands_fail_on_missing_request(self):
        data = {
            'variables': [
                {'type': 'U8'}
            ],
            'commands': [
                {'number': 123, 'reply': [{'name': 'some_variable'}]}
            ]
        }

        with pytest.raises(ValidationError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    DeviceSpec.load('dummy_path')

        self.assertIsNotNone(exception_info.value)

    def test_device_spec_commands_fail_on_missing_reply(self):
        data = {
            'variables': [
                {'type': 'U8'}
            ],
            'commands': [
                {'number': 123, 'request': []}
            ]
        }

        with pytest.raises(ValidationError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    DeviceSpec.load('dummy_path')

        self.assertIsNotNone(exception_info.value)

    def test_device_spec_commands_fail_on_missing_name(self):
        data = {
            'variables': [
                {'type': 'U8'}
            ],
            'commands': [
                {'number': 123, 'reply': [{'name1': 'some_variable'}]}
            ]
        }

        with pytest.raises(ValidationError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    DeviceSpec.load('dummy_path')

        self.assertIsNotNone(exception_info.value)

    def test_device_create(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': [
                {'number': 123, 'request': [], 'reply': [{ 'name': 'some_variable' }]},
                {'number': 4567, 'request': [{'name': 'some_variable'}], 'reply': [{'name': 'some_variable'}, {'name': 'another_variable'}]}
            ]
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                device_spec = DeviceSpec.load('dummy_path')
                target = Device.create(device_spec)
                self.assertEqual(6, len(target.data.keys()))

                self.assertTrue('expanded_device_type' in target.data)
                self.assertEqual(U16, type(target.data['expanded_device_type']))
                self.assertTrue('device_id' in target.data)
                self.assertEqual(U24, type(target.data['device_id']))
                self.assertTrue('polling_address' in target.data)
                self.assertEqual(U8, type(target.data['polling_address']))
                self.assertTrue('some_variable' in target.data)
                self.assertEqual(U8, type(target.data['some_variable']))
                self.assertTrue('another_variable' in target.data)
                self.assertEqual(F32, type(target.data['another_variable']))

                self.assertEqual(2, len(target.commands.keys()))
                self.assertTrue(123 in target.commands)
                self.assertTrue(4567 in target.commands)

                self.assertEqual(63, target.polling_address.get_value())
                self.assertEqual(0x1123456789, target.unique_address, 'Most significant bit must be cleared')

    def test_device_device_id_must_be_u24(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16'},
                {'name': 'device_id', 'type': 'U32'},
                {'name': 'polling_address', 'type': 'U8'},
                {'name': 'response_code', 'type': 'U8'},
            ],
            'commands': []
        }

        with pytest.raises(InvalidDeviceSpecError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    device_spec = DeviceSpec.load('dummy_path')
                    Device.create(device_spec)

        self.assertEqual('device_id must be U24', exception_info.value.message)

    def test_device_expanded_device_type_must_be_u16(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U8'},
                {'name': 'device_id', 'type': 'U24'},
                {'name': 'polling_address', 'type': 'U8'},
                {'name': 'response_code', 'type': 'U8'},
            ],
            'commands': []
        }

        with pytest.raises(InvalidDeviceSpecError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    device_spec = DeviceSpec.load('dummy_path')
                    Device.create(device_spec)

        self.assertEqual('expanded_device_type must be U16', exception_info.value.message)

    def test_device_polling_address_must_be_u8(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16'},
                {'name': 'device_id', 'type': 'U24'},
                {'name': 'polling_address', 'type': 'F32'},
                {'name': 'response_code', 'type': 'U8'},
            ],
            'commands': []
        }

        with pytest.raises(InvalidDeviceSpecError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    device_spec = DeviceSpec.load('dummy_path')
                    Device.create(device_spec)

        self.assertEqual('polling_address must be U8', exception_info.value.message)

    def test_device_response_code_must_be_u8(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16'},
                {'name': 'device_id', 'type': 'U24'},
                {'name': 'polling_address', 'type': 'U8'},
                {'name': 'response_code', 'type': 'U16'},
            ],
            'commands': []
        }

        with pytest.raises(InvalidDeviceSpecError) as exception_info:
            with patch("builtins.open", mock_open(read_data="{}")):
                with patch("json.load", return_value=data):
                    device_spec = DeviceSpec.load('dummy_path')
                    Device.create(device_spec)

        self.assertEqual('response_code must be U8', exception_info.value.message)

    def test_command_dispatcher_should_dispatch_positive_polling_address(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                frame = HartFrame(frame_type=FrameType.STX,command_number=0,is_long_address=False,short_address=63)
                actual = target.should_dispatch(frame)
                self.assertTrue(actual)

    def test_command_dispatcher_should_dispatch_negative_polling_address(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                frame = HartFrame(frame_type=FrameType.STX,command_number=0,is_long_address=False,short_address=61)
                actual = target.should_dispatch(frame)
                self.assertFalse(actual)

    def test_command_dispatcher_should_dispatch_negative_command_number(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                frame = HartFrame(frame_type=FrameType.STX,command_number=1,is_long_address=False,short_address=63)
                actual = target.should_dispatch(frame)
                self.assertFalse(actual)

    def test_command_dispatcher_should_dispatch_positive_long_address(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                frame = HartFrame(frame_type=FrameType.STX,command_number=123,is_long_address=True,long_address=0x1123456789)
                actual = target.should_dispatch(frame)
                self.assertTrue(actual)

    def test_command_dispatcher_should_dispatch_negative_expanded_device_type(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                frame = HartFrame(frame_type=FrameType.STX, command_number=123, is_long_address=True,
                                  long_address=0x1121456789)
                actual = target.should_dispatch(frame)
                self.assertFalse(actual)

    def test_command_dispatcher_should_dispatch_negative_expanded_device_id(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                frame = HartFrame(frame_type=FrameType.STX, command_number=123, is_long_address=True,
                                  long_address=0x1123256789)
                actual = target.should_dispatch(frame)
                self.assertFalse(actual)

    def test_command_dispatcher_should_dispatch_negative_ack(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                frame = HartFrame(frame_type=FrameType.ACK, command_number=123, is_long_address=True,
                                  long_address=0x1123456789)
                actual = target.should_dispatch(frame)
                self.assertFalse(actual)

    def test_command_dispatcher_should_dispatch_negative_back(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8'},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': []
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                frame = HartFrame(frame_type=FrameType.BACK, command_number=123, is_long_address=True,
                                  long_address=0x1123456789)
                actual = target.should_dispatch(frame)
                self.assertFalse(actual)

    def test_command_dispatcher_dispatch_implemented(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'some_variable', 'type': 'U8', 'value': 0x12},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': [
                {'number': 123, 'request': [], 'reply': [{ 'name': 'some_variable' }]},
                {'number': 4567, 'request': [{'name': 'some_variable'}], 'reply': [{'name': 'some_variable'}, {'name': 'another_variable'}]}
            ]
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                expected = (bytearray([0x12]), False)
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                actual = target.dispatch(123)
                self.assertEqual(expected, actual)

    def test_command_dispatcher_dispatch_not_implemented(self):
        data = {
            'variables': [
                {'name': 'expanded_device_type', 'type': 'U16', 'value': 0x9123},
                {'name': 'device_id', 'type': 'U24', 'value': 0x456789},
                {'name': 'polling_address', 'type': 'U8', 'value': 63},
                {'name': 'response_code', 'type': 'U8'},
                {'name': 'device_status', 'type': 'U8', 'value': 0x34},
                {'name': 'some_variable', 'type': 'U8', 'value': 0x12},
                {'name': 'another_variable', 'type': 'F32', 'value': 1.234}
            ],
            'commands': [
                {'number': 123, 'request': [], 'reply': [{ 'name': 'some_variable' }]},
                {'number': 4567, 'request': [{'name': 'some_variable'}], 'reply': [{'name': 'some_variable'}, {'name': 'another_variable'}]}
            ]
        }

        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("json.load", return_value=data):
                expected = (bytearray([0x40,0x34]), False)
                device_spec = DeviceSpec.load('dummy_path')
                device = Device.create(device_spec)
                target = CommandDispatcher(device)
                actual = target.dispatch(121)
                self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
