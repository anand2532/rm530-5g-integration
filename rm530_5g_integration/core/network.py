"""NetworkManager integration."""

import subprocess
from typing import Any, Dict, List, Optional

from rm530_5g_integration.utils.exceptions import NetworkConfigurationError
from rm530_5g_integration.utils.logging import get_logger

logger = get_logger(__name__)


class NetworkManager:
    """Handle NetworkManager configuration for ECM interface."""

    def __init__(self):
        """Initialize NetworkManager handler."""
        self._check_nmcli()

    def _check_nmcli(self) -> None:
        """Check if nmcli is available."""
        try:
            subprocess.run(["nmcli", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise NetworkConfigurationError("NetworkManager (nmcli) not found")

    def connection_exists(self, connection_name: str) -> bool:
        """
        Check if a connection profile exists.

        Args:
            connection_name: Connection profile name

        Returns:
            True if connection exists
        """
        try:
            result = subprocess.run(
                ["nmcli", "connection", "show", connection_name], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking connection: {e}")
            return False

    def create_connection(
        self,
        interface: str = "usb0",
        connection_name: str = "RM530-5G-ECM",
        ipv4_method: str = "auto",
        route_metric: int = 100,
        dns: Optional[List[str]] = None,
        autoconnect: bool = True,
    ) -> bool:
        """
        Create NetworkManager connection profile.

        Args:
            interface: Network interface name
            connection_name: Connection profile name
            ipv4_method: IP configuration method (auto/manual)
            route_metric: Route metric priority
            dns: DNS servers list
            autoconnect: Enable auto-connect

        Returns:
            True if successful
        """
        if self.connection_exists(connection_name):
            logger.info(f"Connection '{connection_name}' already exists")
            return True

        dns_str = " ".join(dns) if dns else "8.8.8.8 1.1.1.1"

        cmd = [
            "nmcli",
            "connection",
            "add",
            "type",
            "ethernet",
            "ifname",
            interface,
            "con-name",
            connection_name,
            "ipv4.method",
            ipv4_method,
            "ipv4.route-metric",
            str(route_metric),
            "ipv4.dns",
            dns_str,
            "connection.autoconnect",
            "yes" if autoconnect else "no",
        ]

        try:
            logger.info(f"Creating NetworkManager connection: {connection_name}")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Connection created successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create connection: {e.stderr}")
            raise NetworkConfigurationError(f"Failed to create connection: {e.stderr}")

    def activate_connection(self, connection_name: str) -> bool:
        """
        Activate a connection.

        Args:
            connection_name: Connection profile name

        Returns:
            True if successful
        """
        try:
            logger.info(f"Activating connection: {connection_name}")
            subprocess.run(
                ["nmcli", "connection", "up", connection_name],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("Connection activated")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to activate connection: {e.stderr}")
            raise NetworkConfigurationError(f"Failed to activate connection: {e.stderr}")

    def get_active_connections(self) -> List[str]:
        """
        Get list of active connection names.

        Returns:
            List of active connection names
        """
        try:
            result = subprocess.run(
                ["nmcli", "connection", "show", "--active"],
                capture_output=True,
                text=True,
                check=True,
            )
            connections = []
            for line in result.stdout.split("\n")[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if parts:
                        connections.append(parts[0])
            return connections
        except Exception as e:
            logger.error(f"Error getting active connections: {e}")
            return []

    def get_interface_ip(self, interface: str) -> Optional[str]:
        """
        Get IP address of an interface.

        Args:
            interface: Interface name

        Returns:
            IP address if found, None otherwise
        """
        try:
            result = subprocess.run(
                ["ip", "addr", "show", interface], capture_output=True, text=True, check=True
            )
            for line in result.stdout.split("\n"):
                if "inet " in line and not "inet 127" in line:
                    parts = line.split()
                    return parts[1].split("/")[0]
            return None
        except Exception:
            return None
