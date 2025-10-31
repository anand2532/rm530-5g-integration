"""Default configuration values."""

from typing import Any, Dict

# Default carrier configurations
DEFAULT_CARRIERS: Dict[str, Dict[str, Any]] = {
    "airtel": {
        "apn": "airtelgprs.com",
        "preferred_interface": "usb0",
        "dns": ["8.8.8.8", "1.1.1.1"],
    },
    "jio": {
        "apn": "jionet",
        "preferred_interface": "usb0",
        "dns": ["8.8.8.8", "1.1.1.1"],
    },
    "vodafone": {
        "apn": "www",
        "preferred_interface": "usb0",
        "dns": ["8.8.8.8", "1.1.1.1"],
    },
    "idea": {
        "apn": "internet",
        "preferred_interface": "usb0",
        "dns": ["8.8.8.8", "1.1.1.1"],
    },
}

# Default network settings
DEFAULT_NETWORK_SETTINGS = {
    "route_metric": 100,
    "autoconnect": True,
    "ipv4_method": "auto",
    "connection_name": "RM530-5G-ECM",
}

# Default modem settings
DEFAULT_MODEM_SETTINGS = {
    "at_baudrate": 115200,
    "timeout": 2,
    "command_timeout": 5,
}
