"""Status command."""

import sys
import argparse

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from rm530_5g_integration.core.manager import RM530Manager
from rm530_5g_integration.utils.logging import setup_logger

logger = setup_logger(__name__)
console = Console() if RICH_AVAILABLE else None


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
            if RICH_AVAILABLE:
                # Create main status table
                table = Table(title="RM530 5G Connection Status", box=box.ROUNDED)
                table.add_column("Property", style="cyan", no_wrap=True)
                table.add_column("Value", style="green")
                
                status_text = "[bold green]✓ Connected[/bold green]" if stats.is_connected else "[bold red]✗ Disconnected[/bold red]"
                table.add_row("Status", status_text)
                table.add_row("Interface", stats.interface)
                
                if stats.ip_address:
                    table.add_row("IP Address", stats.ip_address)
                else:
                    table.add_row("IP Address", "[dim]N/A[/dim]")
                
                # Connection statistics
                if stats.is_connected:
                    if stats.bytes_sent is not None:
                        table.add_row("Bytes Sent", stats._format_bytes(stats.bytes_sent))
                    if stats.bytes_received is not None:
                        table.add_row("Bytes Received", stats._format_bytes(stats.bytes_received))
                    if stats.packets_sent is not None:
                        table.add_row("Packets Sent", f"{stats.packets_sent:,}")
                    if stats.packets_received is not None:
                        table.add_row("Packets Received", f"{stats.packets_received:,}")
                
                console.print(table)
                console.print()
                
                # Internet connectivity check
                if stats.is_connected:
                    internet_status = "[bold green]✓ OK[/bold green]" if manager.verify() else "[bold yellow]⚠ Failed[/bold yellow]"
                    console.print(f"Internet Connectivity: {internet_status}")
                    console.print()
            else:
                # Fallback to plain text
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
        if RICH_AVAILABLE:
            console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")
        else:
            print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
