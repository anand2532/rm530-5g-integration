"""Connection statistics monitoring."""

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from rm530_5g_integration.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectionStats:
    """Connection statistics."""

    interface: str
    ip_address: Optional[str] = None
    bytes_sent: Optional[int] = None
    bytes_received: Optional[int] = None
    packets_sent: Optional[int] = None
    packets_received: Optional[int] = None
    uptime: Optional[timedelta] = None
    is_connected: bool = False

    def __str__(self) -> str:
        """String representation."""
        parts = [f"Interface: {self.interface}"]
        if self.ip_address:
            parts.append(f"IP: {self.ip_address}")
        if self.is_connected:
            parts.append("Status: Connected")
            if self.bytes_sent is not None:
                parts.append(f"Sent: {self._format_bytes(self.bytes_sent)}")
            if self.bytes_received is not None:
                parts.append(f"Received: {self._format_bytes(self.bytes_received)}")
        else:
            parts.append("Status: Disconnected")
        return ", ".join(parts)

    @staticmethod
    def _format_bytes(bytes_count: int) -> str:
        """Format bytes to human-readable format."""
        bytes_value = float(bytes_count)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"


def get_connection_stats(interface: str = "usb0") -> ConnectionStats:
    """
    Get connection statistics for an interface.

    Args:
        interface: Network interface name

    Returns:
        ConnectionStats object
    """
    stats = ConnectionStats(interface=interface)

    try:
        # Get interface IP address
        result = subprocess.run(
            ["ip", "addr", "show", interface], capture_output=True, text=True, check=True
        )

        # Parse IP address
        for line in result.stdout.split("\n"):
            if "inet " in line and not "inet 127" in line:
                parts = line.split()
                stats.ip_address = parts[1].split("/")[0]
                stats.is_connected = True
                break

        # Get interface statistics
        result = subprocess.run(
            ["ip", "-s", "link", "show", interface], capture_output=True, text=True, check=True
        )

        # Parse statistics
        lines = result.stdout.split("\n")
        for i, line in enumerate(lines):
            if "RX:" in line:
                # Parse RX stats
                rx_parts = line.split()
                if len(rx_parts) > 1:
                    try:
                        stats.packets_received = int(rx_parts[1])
                    except ValueError:
                        pass
                # Check next line for bytes
                if i + 1 < len(lines):
                    rx_bytes = re.search(r"(\d+)", lines[i + 1])
                    if rx_bytes:
                        stats.bytes_received = int(rx_bytes.group(1))
            elif "TX:" in line:
                # Parse TX stats
                tx_parts = line.split()
                if len(tx_parts) > 1:
                    try:
                        stats.packets_sent = int(tx_parts[1])
                    except ValueError:
                        pass
                # Check next line for bytes
                if i + 1 < len(lines):
                    tx_bytes = re.search(r"(\d+)", lines[i + 1])
                    if tx_bytes:
                        stats.bytes_sent = int(tx_bytes.group(1))

    except subprocess.CalledProcessError:
        logger.debug(f"Interface {interface} not found or not up")
        stats.is_connected = False
    except Exception as e:
        logger.warning(f"Error getting connection stats: {e}")

    return stats
