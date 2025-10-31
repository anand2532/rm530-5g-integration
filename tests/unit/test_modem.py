"""Unit tests for modem module."""

from unittest.mock import MagicMock, Mock, PropertyMock, patch

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
    def test_modem_connect_success(self, mock_serial_class):
        """Test successful modem connection."""
        # Create a mock that accumulates responses properly
        mock_serial = Mock()
        mock_serial.port = "/dev/ttyUSB0"
        mock_serial.baudrate = 115200
        mock_serial.timeout = 2
        mock_serial.is_open = True

        # Track response buffer
        response_buffer = []

        def mock_read(size=None):
            # Read from buffer
            if response_buffer:
                if size is None:
                    result = b"".join(response_buffer)
                    response_buffer.clear()
                    return result
                else:
                    result = b""
                    while response_buffer and len(result) < size:
                        chunk = response_buffer[0]
                        if len(result) + len(chunk) <= size:
                            result += response_buffer.pop(0)
                        else:
                            needed = size - len(result)
                            result += response_buffer[0][:needed]
                            response_buffer[0] = response_buffer[0][needed:]
                            break
                    return result
            return b""

        def mock_write(data):
            # When AT command is written, queue up OK response
            if b"AT" in data:
                response_buffer.append(b"OK\r\n")

        def mock_flush():
            pass

        mock_serial.read = MagicMock(side_effect=mock_read)
        mock_serial.write = MagicMock(side_effect=mock_write)
        mock_serial.flush = MagicMock(side_effect=mock_flush)

        # Make in_waiting return actual int value
        def get_in_waiting():
            return sum(len(r) for r in response_buffer) if response_buffer else 0

        type(mock_serial).in_waiting = PropertyMock(side_effect=get_in_waiting)

        mock_serial_class.return_value = mock_serial

        modem = Modem(port="/dev/ttyUSB0")
        result = modem.connect()

        assert result is True
        assert modem.serial is not None
        assert mock_serial.write.called

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
    def test_send_command_success(self, mock_serial_class):
        """Test sending AT command successfully."""
        mock_serial = Mock()
        mock_serial.port = "/dev/ttyUSB0"
        mock_serial.baudrate = 115200
        mock_serial.timeout = 2
        mock_serial.is_open = True

        # Response buffer that accumulates responses
        response_buffer = []
        connect_called = False

        def mock_read(size=None):
            if response_buffer:
                if size is None:
                    result = b"".join(response_buffer)
                    response_buffer.clear()
                    return result
                else:
                    result = b""
                    while response_buffer and len(result) < size:
                        chunk = response_buffer[0]
                        if len(result) + len(chunk) <= size:
                            result += response_buffer.pop(0)
                        else:
                            needed = size - len(result)
                            result += response_buffer[0][:needed]
                            response_buffer[0] = response_buffer[0][needed:]
                            break
                    return result
            return b""

        def mock_write(data):
            nonlocal connect_called
            # For connect() - first AT command
            if b"AT" in data and not connect_called:
                response_buffer.append(b"OK\r\n")
                connect_called = True
            # For send_command() - second AT command
            elif b"AT" in data:
                response_buffer.append(b"OK\r\n")

        def mock_flush():
            pass

        mock_serial.read = MagicMock(side_effect=mock_read)
        mock_serial.write = MagicMock(side_effect=mock_write)
        mock_serial.flush = MagicMock(side_effect=mock_flush)

        # Make in_waiting return actual int value
        def get_in_waiting():
            return sum(len(r) for r in response_buffer) if response_buffer else 0

        type(mock_serial).in_waiting = PropertyMock(side_effect=get_in_waiting)

        mock_serial_class.return_value = mock_serial

        modem = Modem(port="/dev/ttyUSB0")
        modem.connect()

        result = modem.send_command("AT")
        assert result is True

    def test_send_command_not_connected(self):
        """Test sending command when not connected."""
        modem = Modem()
        with pytest.raises(SerialCommunicationError):
            modem.send_command("AT")

    @patch("serial.Serial")
    def test_context_manager(self, mock_serial_class):
        """Test Modem as context manager."""
        mock_serial = Mock()
        mock_serial.port = "/dev/ttyUSB0"
        mock_serial.baudrate = 115200
        mock_serial.timeout = 2
        mock_serial.is_open = True

        response_buffer = []

        def mock_read(size=None):
            if response_buffer:
                if size is None:
                    result = b"".join(response_buffer)
                    response_buffer.clear()
                    return result
                else:
                    result = b""
                    while response_buffer and len(result) < size:
                        chunk = response_buffer[0]
                        if len(result) + len(chunk) <= size:
                            result += response_buffer.pop(0)
                        else:
                            needed = size - len(result)
                            result += response_buffer[0][:needed]
                            response_buffer[0] = response_buffer[0][needed:]
                            break
                    return result
            return b""

        def mock_write(data):
            if b"AT" in data:
                response_buffer.append(b"OK\r\n")

        def mock_flush():
            pass

        mock_serial.read = MagicMock(side_effect=mock_read)
        mock_serial.write = MagicMock(side_effect=mock_write)
        mock_serial.flush = MagicMock(side_effect=mock_flush)

        # Make in_waiting return actual int value
        def get_in_waiting():
            return sum(len(r) for r in response_buffer) if response_buffer else 0

        type(mock_serial).in_waiting = PropertyMock(side_effect=get_in_waiting)

        mock_serial_class.return_value = mock_serial

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
