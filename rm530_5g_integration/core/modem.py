"""Modem communication and control."""

import glob
import os
import re
import subprocess
import time
from enum import Enum
from typing import Any, Dict, Optional

import serial

from rm530_5g_integration.utils.exceptions import (
    ModemNotFoundError,
    SerialCommunicationError,
)
from rm530_5g_integration.utils.logging import get_logger

logger = get_logger(__name__)


class ModemMode(Enum):
    """USB mode enumeration for RM530 modem."""

    QMI = 0
    ECM = 1
    MBIM = 2
    RNDIS = 3
    UNKNOWN = -1

    def __str__(self) -> str:
        """Return string representation."""
        return self.name


class Modem:
    """Handle communication with RM530 modem via AT commands."""

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, timeout: int = 2):
        """
        Initialize modem connection.

        Args:
            port: Serial port path (auto-detect if None)
            baudrate: Serial baudrate
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None

    def connect(self) -> bool:
        """
        Connect to modem.

        Returns:
            True if connected successfully
        """
        if self.port is None:
            self.port = find_modem()
            if self.port is None:
                raise ModemNotFoundError("Modem not found")

        try:
            logger.info(f"Connecting to modem at {self.port}")
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(0.5)

            # Test communication
            if not self.send_command("AT"):
                raise SerialCommunicationError("No response from modem")

            return True
        except serial.SerialException as e:
            raise SerialCommunicationError(f"Failed to connect: {e}")

    def disconnect(self) -> None:
        """Close modem connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("Disconnected from modem")

    def send_command(self, command: str, expected: str = "OK", timeout: int = 5) -> bool:
        """
        Send AT command to modem.

        Args:
            command: AT command to send
            expected: Expected response string (default: "OK")
            timeout: Command timeout in seconds

        Returns:
            True if command succeeded
        """
        if not self.serial or not self.serial.is_open:
            raise SerialCommunicationError("Modem not connected")

        try:
            # Send command
            self.serial.write(f"{command}\r\n".encode())
            self.serial.flush()
            time.sleep(0.3)

            # Read response
            start_time = time.time()
            response = b""
            while time.time() - start_time < timeout:
                if self.serial.in_waiting:
                    response += self.serial.read(self.serial.in_waiting)
                    time.sleep(0.1)
                else:
                    time.sleep(0.1)

                # Check for complete response
                response_str = response.decode("utf-8", errors="ignore")
                if expected == "" or expected in response_str or "ERROR" in response_str:
                    break

            response_str = response.decode("utf-8", errors="ignore")
            logger.debug(f"AT Command: {command} -> Response: {response_str.strip()}")

            # Check response
            if expected == "":
                return True
            if expected in response_str:
                return True
            if "ERROR" in response_str:
                logger.error(f"Modem returned ERROR for command: {command}")
                return False

            return False

        except Exception as e:
            logger.error(f"Error sending AT command: {e}")
            raise SerialCommunicationError(f"Command failed: {e}")

    def get_response(self, command: str, timeout: int = 5) -> str:
        """
        Send AT command and return response.

        Args:
            command: AT command to send
            timeout: Command timeout in seconds

        Returns:
            Response string
        """
        if not self.serial or not self.serial.is_open:
            raise SerialCommunicationError("Modem not connected")

        try:
            # Clear buffer
            if self.serial.in_waiting:
                self.serial.read(self.serial.in_waiting)

            # Send command
            self.serial.write(f"{command}\r\n".encode())
            self.serial.flush()
            time.sleep(0.5)

            # Read response
            start_time = time.time()
            response = b""
            while time.time() - start_time < timeout:
                if self.serial.in_waiting:
                    response += self.serial.read(self.serial.in_waiting)
                    time.sleep(0.1)
                else:
                    time.sleep(0.1)

                if b"\r\n" in response[-10:]:  # Check for end of response
                    time.sleep(0.2)  # Wait a bit more

            return response.decode("utf-8", errors="ignore")

        except Exception as e:
            logger.error(f"Error getting response: {e}")
            raise SerialCommunicationError(f"Failed to get response: {e}")

    def get_mode(self) -> ModemMode:
        """
        Get current USB mode of the modem.

        Returns:
            Current ModemMode
        """
        if not self.serial or not self.serial.is_open:
            self.connect()

        try:
            logger.debug("Checking current USB mode")
            if not self.serial:
                raise SerialCommunicationError("Modem not connected")

            response = self.get_response('AT+QCFG="usbnet"', timeout=3)
            logger.debug(f"Mode response: {response.strip()}")

            # Parse response - format: +QCFG: "usbnet",<mode>
            match = re.search(r'\+QCFG:\s*"usbnet",\s*(\d+)', response)
            if match:
                mode_value = int(match.group(1))
                for mode in ModemMode:
                    if mode.value == mode_value:
                        logger.info(f"Current modem mode: {mode}")
                        return mode
                logger.warning(f"Unknown mode value: {mode_value}")
                return ModemMode.UNKNOWN
            else:
                logger.warning("Could not parse mode from response")
                return ModemMode.UNKNOWN

        except Exception as e:
            logger.error(f"Error getting modem mode: {e}")
            return ModemMode.UNKNOWN

    def switch_to_ecm_mode(self, apn: Optional[str] = None) -> bool:
        """
        Switch modem to ECM mode.

        Args:
            apn: APN to configure (optional)

        Returns:
            True if successful
        """
        if not self.serial or not self.serial.is_open:
            self.connect()

        logger.info("Switching modem to ECM mode")

        try:
            # Check current mode
            current_mode = self.get_mode()
            if current_mode == ModemMode.ECM:
                logger.info("Modem is already in ECM mode")
                # Still set APN if provided
                if apn:
                    logger.info(f"Setting APN to: {apn}")
                    self.send_command(f'AT+CGDCONT=1,"IP","{apn}"')
                return True

            logger.info(f"Current mode: {current_mode}, switching to ECM")

            # Switch to ECM mode
            if not self.send_command('AT+QCFG="usbnet",1'):
                logger.error("Failed to set ECM mode")
                return False

            # Configure data interface
            self.send_command('AT+QCFG="data_interface",0,0')

            # Set APN if provided
            if apn:
                logger.info(f"Setting APN to: {apn}")
                self.send_command(f'AT+CGDCONT=1,"IP","{apn}"')

            # Apply settings (reset)
            logger.info("Applying settings and resetting modem")
            self.send_command("AT+CFUN=1,1", expected="", timeout=10)

            logger.info("ECM mode configuration complete")
            return True

        except Exception as e:
            logger.error(f"Error switching to ECM mode: {e}")
            return False

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def detect_usb_modem() -> bool:
    """
    Detect if RM530 modem is present via USB enumeration.

    Returns:
        True if modem is detected
    """
    try:
        # Try using lsusb if available
        result = subprocess.run(
            ["lsusb"], capture_output=True, text=True, timeout=5, check=True
        )
        # Look for Qualcomm or Quectel devices
        if "Qualcomm" in result.stdout or "Quectel" in result.stdout or "RM530" in result.stdout:
            logger.debug("Detected Qualcomm/Quectel device via lsusb")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.debug("lsusb not available or failed")

    try:
        # Try using usb-devices if available
        result = subprocess.run(
            ["usb-devices"], capture_output=True, text=True, timeout=5, check=True
        )
        if "Qualcomm" in result.stdout or "Quectel" in result.stdout or "RM530" in result.stdout:
            logger.debug("Detected Qualcomm/Quectel device via usb-devices")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.debug("usb-devices not available or failed")

    # Try checking sys/bus/usb/devices
    try:
        if os.path.exists("/sys/bus/usb/devices"):
            for entry in os.listdir("/sys/bus/usb/devices"):
                if entry.startswith("usb"):
                    try:
                        manufacturer = os.path.join("/sys/bus/usb/devices", entry, "manufacturer")
                        product = os.path.join("/sys/bus/usb/devices", entry, "product")
                        if os.path.exists(manufacturer) and os.path.exists(product):
                            with open(manufacturer) as f:
                                mfg = f.read().strip()
                            with open(product) as f:
                                prod = f.read().strip()
                            if "Qualcomm" in mfg or "Quectel" in mfg or "RM530" in prod:
                                logger.debug(f"Detected USB device: {mfg} {prod}")
                                return True
                    except (IOError, OSError):
                        continue
    except (PermissionError, OSError):
        logger.debug("Could not access /sys/bus/usb/devices")

    # Check for network interfaces that might indicate modem
    try:
        result = subprocess.run(
            ["ip", "link", "show"], capture_output=True, text=True, timeout=5, check=True
        )
        # Look for usb0, wwan0, wwp0s* interfaces
        if any(iface in result.stdout for iface in ["usb0", "wwan0"]) or "wwp" in result.stdout:
            logger.debug("Detected potential modem interface")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.debug("ip command not available or failed")

    return False


def find_modem() -> Optional[str]:
    """
    Find the Qualcomm modem's AT command port.

    Uses multiple strategies:
    1. Check for USB device presence
    2. Try all /dev/ttyUSB* ports
    3. Check for CDC-ACM devices

    Returns:
        Port path if found, None otherwise
    """
    # First check if modem is present at all
    if not detect_usb_modem():
        logger.debug("No USB modem detected")

    ports = glob.glob("/dev/ttyUSB*")

    if not ports:
        logger.warning("No /dev/ttyUSB* devices found")
        # Also check for CDC-ACM devices
        ports.extend(glob.glob("/dev/ttyACM*"))
        if not ports:
            logger.warning("No serial modem interfaces found")
            return None

    logger.debug(f"Found {len(ports)} serial ports: {', '.join(sorted(ports))}")

    # Try likely AT command ports first (usually ttyUSB2 in QMI/ECM, ttyUSB1 in MBIM)
    # In ECM mode, AT port is often different
    preferred_ports = [
        "/dev/ttyUSB2",
        "/dev/ttyUSB3",
        "/dev/ttyUSB1",
        "/dev/ttyUSB0",
        "/dev/ttyUSB4",
        "/dev/ttyUSB5",
        "/dev/ttyACM0",
        "/dev/ttyACM1",
    ]
    all_ports = [p for p in preferred_ports if p in ports] + [
        p for p in ports if p not in preferred_ports
    ]

    for port in all_ports:
        try:
            logger.debug(f"Testing {port}...")
            ser = serial.Serial(port, 115200, timeout=2)
            time.sleep(0.3)

            # Clear buffer
            if ser.in_waiting:
                ser.read(ser.in_waiting)

            # Send AT command
            ser.write(b"AT\r\n")
            ser.flush()
            time.sleep(0.8)

            # Read response
            response = ser.read(100).decode("utf-8", errors="ignore")
            ser.close()

            if "OK" in response:
                logger.info(f"Found modem at: {port}")
                return port

        except (serial.SerialException, PermissionError) as e:
            logger.debug(f"Port {port} error: {e}")
            continue

    logger.warning("No modem found responding to AT commands")
    return None
