"""Configuration validation utilities."""

import re
from typing import Any, Dict, List, Optional

from rm530_5g_integration.utils.exceptions import ConfigurationError
from rm530_5g_integration.utils.logging import get_logger

logger = get_logger(__name__)


class ConfigValidator:
    """Validate configuration settings."""

    @staticmethod
    def validate_apn(apn: str) -> bool:
        """
        Validate APN format.

        Args:
            apn: APN string to validate

        Returns:
            True if valid

        Raises:
            ConfigurationError: If APN is invalid
        """
        if not apn or not isinstance(apn, str):
            raise ConfigurationError("APN must be a non-empty string")

        if len(apn) > 100:
            raise ConfigurationError("APN must be 100 characters or less")

        # APN can contain alphanumeric, dots, dashes, underscores
        if not re.match(r"^[a-zA-Z0-9._-]+$", apn):
            raise ConfigurationError(
                "APN can only contain alphanumeric characters, dots, dashes, and underscores"
            )

        return True

    @staticmethod
    def validate_interface(interface: str) -> bool:
        """
        Validate network interface name.

        Args:
            interface: Interface name to validate

        Returns:
            True if valid

        Raises:
            ConfigurationError: If interface name is invalid
        """
        if not interface or not isinstance(interface, str):
            raise ConfigurationError("Interface name must be a non-empty string")

        # Linux interface names: 1-15 characters, alphanumeric + underscores
        if not re.match(r"^[a-zA-Z0-9_]{1,15}$", interface):
            raise ConfigurationError(
                "Interface name must be 1-15 alphanumeric characters or underscores"
            )

        return True

    @staticmethod
    def validate_dns(dns: List[str]) -> bool:
        """
        Validate DNS server list.

        Args:
            dns: List of DNS server IP addresses

        Returns:
            True if valid

        Raises:
            ConfigurationError: If DNS list is invalid
        """
        if not isinstance(dns, list):
            raise ConfigurationError("DNS must be a list")

        if len(dns) == 0:
            raise ConfigurationError("At least one DNS server must be specified")

        if len(dns) > 3:
            logger.warning("More than 3 DNS servers specified, only first 3 will be used")

        ip_pattern = re.compile(
            r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )

        for i, dns_server in enumerate(dns[:3]):  # Validate first 3
            if not isinstance(dns_server, str):
                raise ConfigurationError(f"DNS server {i+1} must be a string")

            if not ip_pattern.match(dns_server):
                raise ConfigurationError(
                    f"DNS server {i+1} '{dns_server}' is not a valid IP address"
                )

        return True

    @staticmethod
    def validate_baudrate(baudrate: int) -> bool:
        """
        Validate serial baudrate.

        Args:
            baudrate: Baudrate value

        Returns:
            True if valid

        Raises:
            ConfigurationError: If baudrate is invalid
        """
        valid_baudrates = [9600, 19200, 38400, 57600, 115200, 230400]

        if not isinstance(baudrate, int):
            raise ConfigurationError("Baudrate must be an integer")

        if baudrate not in valid_baudrates:
            raise ConfigurationError(
                f"Baudrate must be one of: {', '.join(map(str, valid_baudrates))}"
            )

        return True

    @staticmethod
    def validate_carrier_config(carrier: str, config: Dict[str, Any]) -> bool:
        """
        Validate carrier configuration.

        Args:
            carrier: Carrier name
            config: Carrier configuration dictionary

        Returns:
            True if valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not carrier or not isinstance(carrier, str):
            raise ConfigurationError("Carrier name must be a non-empty string")

        # Validate required fields
        if "apn" not in config:
            raise ConfigurationError(f"Carrier '{carrier}' missing required field: apn")

        # Validate APN
        ConfigValidator.validate_apn(config["apn"])

        # Validate optional fields if present
        if "preferred_interface" in config:
            ConfigValidator.validate_interface(config["preferred_interface"])

        if "dns" in config:
            ConfigValidator.validate_dns(config["dns"])

        return True

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate entire configuration dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            # Validate carriers
            if "carriers" in config:
                carriers = config["carriers"]
                if not isinstance(carriers, dict):
                    errors.append("'carriers' must be a dictionary")
                else:
                    for carrier, carrier_config in carriers.items():
                        try:
                            ConfigValidator.validate_carrier_config(carrier, carrier_config)
                        except ConfigurationError as e:
                            errors.append(f"Carrier '{carrier}': {str(e)}")

            # Validate defaults
            if "defaults" in config:
                defaults = config["defaults"]
                if not isinstance(defaults, dict):
                    errors.append("'defaults' must be a dictionary")
                else:
                    if "preferred_interface" in defaults:
                        try:
                            ConfigValidator.validate_interface(defaults["preferred_interface"])
                        except ConfigurationError as e:
                            errors.append(f"Defaults: {str(e)}")

                    if "dns" in defaults:
                        try:
                            ConfigValidator.validate_dns(defaults["dns"])
                        except ConfigurationError as e:
                            errors.append(f"Defaults: {str(e)}")

            # Validate modem settings
            if "modem" in config:
                modem_settings = config["modem"]
                if not isinstance(modem_settings, dict):
                    errors.append("'modem' must be a dictionary")
                else:
                    if "at_baudrate" in modem_settings:
                        try:
                            ConfigValidator.validate_baudrate(modem_settings["at_baudrate"])
                        except ConfigurationError as e:
                            errors.append(f"Modem settings: {str(e)}")

        except Exception as e:
            errors.append(f"Unexpected validation error: {str(e)}")

        return errors


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration and raise exception if invalid.

    Args:
        config: Configuration dictionary

    Raises:
        ConfigurationError: If configuration is invalid
    """
    errors = ConfigValidator.validate_config(config)
    if errors:
        error_message = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ConfigurationError(error_message)
