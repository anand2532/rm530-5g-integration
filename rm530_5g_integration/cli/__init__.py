"""CLI commands for RM530 5G Integration."""

from rm530_5g_integration.cli.setup import main as setup_main
from rm530_5g_integration.cli.status import main as status_main
from rm530_5g_integration.cli.signal import main as signal_main

__all__ = [
    "setup_main",
    "status_main",
    "signal_main",
]

