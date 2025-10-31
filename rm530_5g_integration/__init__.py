"""
RM530 5G Integration Package

Integration tools for Waveshare RM530 5G modem with Raspberry Pi using ECM mode.
"""

__version__ = "3.0.1"
__author__ = "Anand"
__email__ = "anand@example.com"
__description__ = "Integration tools and scripts for Waveshare RM530 5G modem with Raspberry Pi"

# Import main classes for easy access
from rm530_5g_integration.core.manager import RM530Manager
from rm530_5g_integration.core.modem import Modem
from rm530_5g_integration.core.network import NetworkManager
from rm530_5g_integration.core.health import HealthMonitor, HealthStatus
from rm530_5g_integration.monitoring import SignalQuality, ConnectionStats

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "RM530Manager",
    "Modem",
    "NetworkManager",
    "HealthMonitor",
    "HealthStatus",
    "SignalQuality",
    "ConnectionStats",
]

