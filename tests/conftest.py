"""Pytest configuration and fixtures."""

from typing import Generator
from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def mock_serial():
    """Mock serial.Serial instance."""
    serial_mock = Mock()
    serial_mock.port = "/dev/ttyUSB2"
    serial_mock.baudrate = 115200
    serial_mock.timeout = 2
    serial_mock.is_open = True
    serial_mock.in_waiting = 0
    serial_mock.read.return_value = b"OK\r\n"
    serial_mock.write.return_value = None

    def mock_read(size=None):
        return b"OK\r\n"

    serial_mock.read = MagicMock(side_effect=mock_read)
    return serial_mock


@pytest.fixture
def mock_modem_port():
    """Mock modem port path."""
    return "/dev/ttyUSB2"


@pytest.fixture
def mock_subprocess_result():
    """Mock subprocess.run result."""
    result = Mock()
    result.returncode = 0
    result.stdout = "test output"
    result.stderr = ""
    return result


@pytest.fixture
def sample_config():
    """Sample configuration dictionary."""
    return {
        "carriers": {
            "airtel": {
                "apn": "airtelgprs.com",
                "preferred_interface": "usb0",
                "dns": ["8.8.8.8", "1.1.1.1"],
            },
            "jio": {"apn": "jionet", "preferred_interface": "usb0", "dns": ["8.8.8.8", "1.1.1.1"]},
        },
        "defaults": {
            "route_metric": 100,
            "autoconnect": True,
            "ipv4_method": "auto",
            "connection_name": "RM530-5G-ECM",
        },
        "modem": {"at_baudrate": 115200, "timeout": 2},
    }
