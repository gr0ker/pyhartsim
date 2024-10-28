import serial
import unittest

from hartsim.datalink import create_port
from unittest.mock import patch, MagicMock


class TestDataLink(unittest.TestCase):

    def test_port_created(self):
        mock_serial_instance = MagicMock()

        with patch("serial.Serial", return_value=mock_serial_instance) as mock_serial_class:
            create_port('dummy_port')

            mock_serial_class.assert_called_once_with('dummy_port',
                baudrate=1200,
                parity=serial.PARITY_ODD,
                bytesize=8,
                stopbits=1)

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
