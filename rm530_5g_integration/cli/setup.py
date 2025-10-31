"""Unified setup command."""

import sys
import os
import time
import argparse

from rm530_5g_integration.core.manager import RM530Manager
from rm530_5g_integration.utils.exceptions import RM530Error
from rm530_5g_integration.utils.logging import setup_logger

logger = setup_logger(__name__)


def main():
    """Main CLI entry point for unified setup."""
    parser = argparse.ArgumentParser(
        description="Complete RM530 5G modem setup (ECM mode + NetworkManager)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup with APN
  sudo rm530-setup --apn airtelgprs.com

  # Setup with carrier name (uses config file)
  sudo rm530-setup --carrier airtel

  # Setup without auto-activation
  sudo rm530-setup --apn airtelgprs.com --no-activate
        """
    )
    
    parser.add_argument(
        "--apn",
        help="APN name (e.g., airtelgprs.com, jionet)"
    )
    parser.add_argument(
        "--carrier",
        choices=["airtel", "jio", "vodafone", "idea"],
        help="Carrier name (uses config file for APN and settings)"
    )
    parser.add_argument(
        "--interface", "-i",
        default="usb0",
        help="Network interface name (default: usb0)"
    )
    parser.add_argument(
        "--no-activate",
        action="store_true",
        help="Don't activate connection after setup"
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for modem restart"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Check root access
    if os.geteuid() != 0:
        print("✗ This command must be run as root (sudo)")
        sys.exit(1)
    
    # Set logging level
    if args.verbose:
        logger.setLevel("DEBUG")
    
    # Validate arguments
    if not args.apn and not args.carrier:
        parser.error("Either --apn or --carrier must be specified")
    
    try:
        print("=" * 60)
        print("RM530 5G Modem - Complete Setup")
        print("=" * 60)
        print()
        
        manager = RM530Manager()
        success = manager.setup(
            apn=args.apn,
            carrier=args.carrier,
            interface=args.interface,
            activate=not args.no_activate,
            wait_restart=not args.no_wait
        )
        
        if success:
            print()
            print("=" * 60)
            print("✓ Setup Complete!")
            print("=" * 60)
            
            if not args.no_activate:
                # Show status
                time.sleep(2)  # Give connection time to establish
                status = manager.status(args.interface)
                if status.is_connected:
                    print(f"✓ Connected: {status.ip_address}")
                else:
                    print("⚠ Connection may still be establishing...")
                    print(f"  Run 'rm530-status' to check status")
            else:
                print(f"\nTo activate connection:")
                print(f"  sudo nmcli connection up RM530-5G-ECM")
            
            print()
        else:
            print()
            print("=" * 60)
            print("✗ Setup Failed!")
            print("=" * 60)
            sys.exit(1)
            
    except RM530Error as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

