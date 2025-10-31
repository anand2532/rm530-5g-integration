"""Status command."""

import sys
import argparse

from rm530_5g_integration.core.manager import RM530Manager
from rm530_5g_integration.utils.logging import setup_logger

logger = setup_logger(__name__)


def main():
    """CLI entry point for status command."""
    parser = argparse.ArgumentParser(
        description="Check RM530 5G connection status"
    )
    parser.add_argument(
        "--interface", "-i",
        default="usb0",
        help="Network interface name (default: usb0)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    try:
        manager = RM530Manager()
        stats = manager.status(args.interface)
        
        if args.json:
            import json
            output = {
                "interface": stats.interface,
                "connected": stats.is_connected,
                "ip_address": stats.ip_address,
                "bytes_sent": stats.bytes_sent,
                "bytes_received": stats.bytes_received,
                "packets_sent": stats.packets_sent,
                "packets_received": stats.packets_received,
            }
            print(json.dumps(output, indent=2))
        else:
            print("=" * 60)
            print("RM530 5G Connection Status")
            print("=" * 60)
            print()
            print(f"Interface: {stats.interface}")
            print(f"Status: {'✓ Connected' if stats.is_connected else '✗ Disconnected'}")
            if stats.ip_address:
                print(f"IP Address: {stats.ip_address}")
            if stats.bytes_sent is not None:
                print(f"Bytes Sent: {stats._format_bytes(stats.bytes_sent)}")
            if stats.bytes_received is not None:
                print(f"Bytes Received: {stats._format_bytes(stats.bytes_received)}")
            if stats.packets_sent is not None:
                print(f"Packets Sent: {stats.packets_sent}")
            if stats.packets_received is not None:
                print(f"Packets Received: {stats.packets_received}")
            
            # Verify connectivity
            if stats.is_connected:
                if manager.verify():
                    print("\n✓ Internet connectivity: OK")
                else:
                    print("\n⚠ Internet connectivity: Failed")
            
            print()
            
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

