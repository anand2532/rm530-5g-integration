"""Main manager class for RM530 5G operations."""

import time
import subprocess
from typing import Optional, Dict, Any

from rm530_5g_integration.core.modem import Modem, find_modem
from rm530_5g_integration.core.network import NetworkManager as NMManager
from rm530_5g_integration.config import ConfigLoader
from rm530_5g_integration.monitoring import SignalQuality, get_signal_quality, ConnectionStats, get_connection_stats
from rm530_5g_integration.utils.exceptions import RM530Error, ModemNotFoundError
from rm530_5g_integration.utils.logging import get_logger

logger = get_logger(__name__)


class RM530Manager:
    """
    Main manager class for RM530 5G modem operations.
    
    Provides a unified API for setup, configuration, and monitoring.
    
    Examples:
        >>> manager = RM530Manager()
        >>> manager.setup(apn="airtelgprs.com", carrier="airtel")
        True
        >>> status = manager.status()
        >>> print(status.ip_address)
        '192.168.1.100'
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize RM530 manager.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = ConfigLoader(config_path)
        self.modem: Optional[Modem] = None
        self.network = NMManager()
        self._defaults = self.config.get_defaults()
        self._modem_settings = self.config.get_modem_settings()
    
    def setup(
        self,
        apn: Optional[str] = None,
        carrier: Optional[str] = None,
        interface: Optional[str] = None,
        activate: bool = True,
        wait_restart: bool = True
    ) -> bool:
        """
        Complete setup: switch to ECM mode and configure network.
        
        Args:
            apn: APN name (optional, will use carrier config if carrier specified)
            carrier: Carrier name (e.g., 'airtel', 'jio') - uses config file
            interface: Network interface name (default: auto-detect)
            activate: Activate connection after configuration
            wait_restart: Wait for modem restart after ECM switch
        
        Returns:
            True if setup successful
        """
        logger.info("Starting RM530 setup")
        
        # Get APN and settings from carrier config if specified
        if carrier:
            carrier_config = self.config.get_carrier_config(carrier)
            if not apn:
                apn = carrier_config.get("apn")
            if not interface:
                interface = carrier_config.get("preferred_interface")
        
        if not apn:
            raise RM530Error("APN must be specified or carrier must be provided")
        
        interface = interface or self._defaults.get("preferred_interface", "usb0")
        connection_name = self._defaults.get("connection_name", "RM530-5G-ECM")
        
        try:
            # Step 1: Switch to ECM mode
            logger.info(f"Switching modem to ECM mode with APN: {apn}")
            self.modem = Modem(baudrate=self._modem_settings["at_baudrate"])
            self.modem.connect()
            
            if not self.modem.switch_to_ecm_mode(apn=apn):
                logger.error("Failed to switch to ECM mode")
                return False
            
            self.modem.disconnect()
            
            if wait_restart:
                logger.info("Waiting for modem to restart (15 seconds)...")
                time.sleep(15)
            
            # Step 2: Configure NetworkManager
            carrier_config = self.config.get_carrier_config(carrier) if carrier else {}
            dns = carrier_config.get("dns") or self._defaults.get("dns", ["8.8.8.8", "1.1.1.1"])
            
            logger.info(f"Configuring NetworkManager for interface: {interface}")
            self.network.create_connection(
                interface=interface,
                connection_name=connection_name,
                ipv4_method=self._defaults.get("ipv4_method", "auto"),
                route_metric=self._defaults.get("route_metric", 100),
                dns=dns,
                autoconnect=self._defaults.get("autoconnect", True)
            )
            
            # Step 3: Activate connection
            if activate:
                logger.info("Activating connection")
                self.network.activate_connection(connection_name)
            
            logger.info("Setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise RM530Error(f"Setup failed: {e}")
    
    def status(self, interface: str = "usb0") -> ConnectionStats:
        """
        Get current connection status.
        
        Args:
            interface: Network interface name
        
        Returns:
            ConnectionStats object
        """
        return get_connection_stats(interface)
    
    def signal_quality(self) -> SignalQuality:
        """
        Get signal quality metrics.
        
        Returns:
            SignalQuality object
        """
        if not self.modem:
            self.modem = Modem(baudrate=self._modem_settings["at_baudrate"])
            self.modem.connect()
        
        try:
            return get_signal_quality(self.modem)
        finally:
            # Don't disconnect if we didn't create the connection
            pass
    
    def disconnect(self) -> bool:
        """
        Disconnect from network.
        
        Returns:
            True if successful
        """
        connection_name = self._defaults.get("connection_name", "RM530-5G-ECM")
        try:
            logger.info(f"Disconnecting: {connection_name}")
            subprocess.run(
                ["nmcli", "connection", "down", connection_name],
                check=True,
                capture_output=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect: {e}")
            return False
    
    def reconnect(self) -> bool:
        """
        Reconnect to network.
        
        Returns:
            True if successful
        """
        connection_name = self._defaults.get("connection_name", "RM530-5G-ECM")
        return self.network.activate_connection(connection_name)
    
    def verify(self) -> bool:
        """
        Verify connection is working.
        
        Returns:
            True if connection is active
        """
        stats = self.status()
        if not stats.is_connected or not stats.ip_address:
            return False
        
        # Try to ping a reliable server
        import subprocess
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

