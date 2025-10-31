"""Unit tests for modem module."""

from unittest.mock import MagicMock, Mock, patch

import pytest
import serial

from rm530_5g_integration.core.modem import Modem, find_modem
from rm530_5g_integration.utils.exceptions import ModemNotFoundError, SerialCommunicationError


class TestModem:
    """Test Modem class."""

    def test_modem_init(self):
        """Test Modem initialization."""
        modem = Modem(port="/dev/ttyUSB0", baudrate=115200, timeout=2)
        assert modem.port == "/dev/ttyUSB0"
        assert modem.baudrate == 115200
        assert modem.timeout == 2
        assert modem.serial is None

    def test_modem_init_auto_port(self):
        """Test Modem initialization without port."""
        modem = Modem()
        assert modem.port is None
        assert modem.serial is None

    @patch("serial.Serial")
    def test_modem_connect_success(self, mock_serial_class, mock_serial):
        """Test successful modem connection."""
        mock_serial_class.return_value = mock_serial
        mock_serial.in_waiting = 0
        mock_serial.read.return_value = b"OK\r\n"
        mock_serial.is_open = True

        modem = Modem(port="/dev/ttyUSB0")
        result = modem.connect()

        assert result is True
        assert modem.serial is not None
        mock_serial.write.assert_called()

    @patch("serial.Serial")
    def test_modem_connect_failure(self, mock_serial_class):
        """Test modem connection failure."""
        mock_serial_class.side_effect = serial.SerialException("Port not found")

        modem = Modem(port="/dev/ttyUSB0")
        with pytest.raises(SerialCommunicationError):
            modem.connect()

    def test_modem_connect_no_port(self):
        """Test connection without port specified."""
        modem = Modem()
        with patch("rm530_5g_integration.core.modem.find_modem", return_value=None):
            with pytest.raises(ModemNotFoundError):
                modem.connect()

    def test_modem_disconnect(self, mock_serial):
        """Test modem disconnection."""
        modem = Modem(port="/dev/ttyUSB0")
        modem.serial = mock_serial
        modem.disconnect()

        mock_serial.close.assert_called_once()

    def test_modem_disconnect_not_connected(self):
        """Test disconnection when not connected."""
        modem = Modem()
        # Should not raise
        modem.disconnect()

    @patch("serial.Serial")
    def test_send_command_success(self, mock_serial_class, mock_serial):
        """Test sending AT command successfully."""
        mock_serial_class.return_value = mock_serial
        mock_serial.in_waiting = 0
        mock_serial.read.return_value = b"OK\r\n"
        mock_serial.is_open = True

        modem = Modem(port="/dev/ttyUSB0")
        modem.connect()

        result = modem.send_command("AT")
        assert result is True

    def test_send_command_not_connected(self):
        """Test sending command when not connected."""
        modem = Modem()
        with pytest.raises(SerialCommunicationError):
            modem.send_command("AT")

    def test_context_manager(self, mock_serial):
        """Test Modem as context manager."""
        with patch("serial.Serial", return_value=mock_serial):
            with Modem(port="/dev/ttyUSB0") as modem:
                assert modem.serial is not None
                assert modem.serial.is_open is True

        # Should be disconnected after context exit
        mock_serial.close.assert_called()


class TestFindModem:
    """Test find_modem function."""

    @patch("glob.glob")
    @patch("serial.Serial")
    def test_find_modem_success(self, mock_serial_class, mock_glob):
        """Test finding modem successfully."""
        mock_glob.return_value = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2"]

        mock_ser = Mock()
        mock_ser.in_waiting = 0
        mock_ser.read.return_value = b"OK\r\n"
        mock_serial_class.return_value = mock_ser

        port = find_modem()
        assert port == "/dev/ttyUSB2"

    @patch("glob.glob")
    def test_find_modem_not_found(self, mock_glob):
        """Test when no modem is found."""
        mock_glob.return_value = []

        port = find_modem()
        assert port is None

    @patch("glob.glob")
    @patch("serial.Serial")
    def test_find_modem_no_response(self, mock_serial_class, mock_glob):
        """Test when ports exist but don't respond."""
        mock_glob.return_value = ["/dev/ttyUSB0"]

        mock_ser = Mock()
        mock_ser.in_waiting = 0
        mock_ser.read.return_value = b"ERROR\r\n"
        mock_serial_class.return_value = mock_ser

        port = find_modem()
        assert port is None
