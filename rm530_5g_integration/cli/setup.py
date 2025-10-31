"""Unified setup command."""

import argparse
import os
import sys
import time

try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from rm530_5g_integration.core.manager import RM530Manager
from rm530_5g_integration.core.modem import Modem, ModemMode, detect_usb_modem, find_modem
from rm530_5g_integration.utils.exceptions import ModemNotFoundError, RM530Error
from rm530_5g_integration.utils.logging import setup_logger

logger = setup_logger(__name__)
console = Console() if RICH_AVAILABLE else None


def print_header(text: str) -> None:
    """Print formatted header."""
    if RICH_AVAILABLE and console is not None:
        console.print(Panel(text, style="bold blue", box=box.DOUBLE))
    else:
        print("=" * 60)
        print(text)
        print("=" * 60)


def print_success(text: str) -> None:
    """Print success message."""
    if RICH_AVAILABLE and console is not None:
        console.print(f"[bold green]✓[/bold green] {text}")
    else:
        print(f"✓ {text}")


def print_error(text: str) -> None:
    """Print error message."""
    if RICH_AVAILABLE and console is not None:
        console.print(f"[bold red]✗[/bold red] {text}")
    else:
        print(f"✗ {text}")


def print_warning(text: str) -> None:
    """Print warning message."""
    if RICH_AVAILABLE and console is not None:
        console.print(f"[bold yellow]⚠[/bold yellow] {text}")
    else:
        print(f"⚠ {text}")


def print_info(text: str) -> None:
    """Print info message."""
    if RICH_AVAILABLE and console is not None:
        console.print(f"[cyan]ℹ[/cyan] {text}")
    else:
        print(f"ℹ {text}")


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
        """,
    )

    parser.add_argument("--apn", help="APN name (e.g., airtelgprs.com, jionet)")
    parser.add_argument(
        "--carrier",
        choices=["airtel", "jio", "vodafone", "idea"],
        help="Carrier name (uses config file for APN and settings)",
    )
    parser.add_argument(
        "--interface", "-i", default="usb0", help="Network interface name (default: usb0)"
    )
    parser.add_argument(
        "--no-activate", action="store_true", help="Don't activate connection after setup"
    )
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for modem restart")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Check root access
    if os.geteuid() != 0:
        print_error("This command must be run as root (sudo)")
        sys.exit(1)

    # Set logging level
    if args.verbose:
        logger.setLevel("DEBUG")

    # Validate arguments
    if not args.apn and not args.carrier:
        parser.error("Either --apn or --carrier must be specified")

    try:
        print_header("RM530 5G Modem - Complete Setup")
        console.print() if RICH_AVAILABLE else print()

        manager = RM530Manager()

        # Step 1: Finding modem
        print_info("Step 1/4: Detecting modem...")
        if RICH_AVAILABLE and console is not None:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Checking for USB modem...", total=None)
                
                # Check USB presence first
                usb_present = detect_usb_modem()
                progress.update(task, description="Searching AT command ports...")
                time.sleep(0.3)
                
                # Try to find AT port
                at_port = find_modem()
                progress.update(task, completed=100)
        else:
            print("Checking for USB modem...")
            usb_present = detect_usb_modem()
            print("Searching AT command ports...")
            at_port = find_modem()

        if not usb_present:
            print_warning("USB modem not detected. Please check:")
            print_info("  - Is the modem connected to USB port?")
            print_info("  - Is the modem powered on?")
            print_info("  - Try: lsusb | grep -i qualcomm")
            console.print() if RICH_AVAILABLE else print()

        if not at_port:
            print_error("No modem found responding to AT commands")
            print_info("\nPossible reasons:")
            print_info("  1. Modem is in wrong USB mode")
            print_info("  2. Modem needs driver installation")
            print_info("  3. Wrong serial port permissions")
            console.print() if RICH_AVAILABLE else print()
            print_info("Attempting setup anyway (modem may restart into AT mode)...")
        else:
            print_success(f"Modem found at: {at_port}")
            
            # Step 1.5: Check current mode
            print_info("Checking current mode...")
            try:
                test_modem = Modem(port=at_port)
                if test_modem.connect():
                    current_mode = test_modem.get_mode()
                    test_modem.disconnect()
                    print_info(f"Current mode: {current_mode}")
                    if current_mode == ModemMode.ECM:
                        print_success("Modem is already in ECM mode!")
                    elif current_mode == ModemMode.UNKNOWN:
                        print_warning("Could not determine modem mode")
                    else:
                        print_info(f"Will switch from {current_mode} to ECM mode")
            except Exception as e:
                logger.debug(f"Could not check mode: {e}")
                print_info("Will attempt to switch to ECM mode anyway")
            
            console.print() if RICH_AVAILABLE else print()

        # Step 2: Switching to ECM mode
        print_info("Step 2/4: Configuring modem...")
        if RICH_AVAILABLE and console is not None:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Configuring modem settings...", total=100)
                time.sleep(0.5)
                progress.update(task, completed=100)
        else:
            print("Configuring modem settings...")

        success = manager.setup(
            apn=args.apn,
            carrier=args.carrier,
            interface=args.interface,
            activate=not args.no_activate,
            wait_restart=not args.no_wait,
        )

        if success:
            print_success("Setup Complete!")
            console.print() if RICH_AVAILABLE else print()

            if not args.no_activate:
                # Show status
                if RICH_AVAILABLE:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                    ) as progress:
                        progress.add_task("Waiting for connection...", total=None)
                        time.sleep(2)
                else:
                    print("Waiting for connection...")
                    time.sleep(2)

                status = manager.status(args.interface)
                if status.is_connected:
                    # Create status table
                    if RICH_AVAILABLE:
                        table = Table(title="Connection Status", box=box.ROUNDED)
                        table.add_column("Property", style="cyan")
                        table.add_column("Value", style="green")
                        table.add_row("Status", "Connected")
                        table.add_row("IP Address", status.ip_address or "N/A")
                        console.print(table)
                    else:
                        print(f"✓ Connected: {status.ip_address}")
                else:
                    print_warning("Connection may still be establishing...")
                    print_info("Run 'rm530-status' to check status")
            else:
                print_info("To activate connection:")
                if RICH_AVAILABLE:
                    console.print("  [bold]sudo nmcli connection up RM530-5G-ECM[/bold]")
                else:
                    print("  sudo nmcli connection up RM530-5G-ECM")

            console.print() if RICH_AVAILABLE else print()
        else:
            print_error("Setup Failed!")
            sys.exit(1)

    except ModemNotFoundError as e:
        print_error(f"Modem not found: {str(e)}")
        print_info("\nTroubleshooting steps:")
        print_info("  1. Check if modem is connected: lsusb | grep -i qualcomm")
        print_info("  2. Try restarting the modem or replugging the USB cable")
        print_info("  3. Check permissions: sudo usermod -aG dialout $USER (then log out/in)")
        print_info("  4. Check if ModemManager is interfering: sudo systemctl stop ModemManager")
        console.print() if RICH_AVAILABLE else print()
        sys.exit(1)
    except RM530Error as e:
        if RICH_AVAILABLE:
            console.print(
                Panel(
                    f"[bold red]Error:[/bold red] {str(e)}",
                    title="Setup Failed",
                    border_style="red",
                )
            )
        else:
            print(f"\n✗ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print_warning("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(
                Panel(
                    f"[bold red]Unexpected Error:[/bold red] {str(e)}",
                    title="Setup Failed",
                    border_style="red",
                )
            )
            if args.verbose:
                import traceback

                console.print_exception()
        else:
            print(f"\n✗ Unexpected error: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
