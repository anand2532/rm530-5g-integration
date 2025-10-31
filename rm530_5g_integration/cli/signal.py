"""Signal quality command."""

import sys
import os
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
from rm530_5g_integration.utils.exceptions import RM530Error
from rm530_5g_integration.utils.logging import setup_logger

logger = setup_logger(__name__)
console = Console() if RICH_AVAILABLE else None


def get_signal_quality_label(rssi: int) -> tuple[str, str]:
    """Get signal quality label and color."""
    if rssi >= -70:
        return "Excellent", "green"
    elif rssi >= -85:
        return "Good", "green"
    elif rssi >= -100:
        return "Fair", "yellow"
    else:
        return "Poor", "red"


def main():
    """CLI entry point for signal quality command."""
    parser = argparse.ArgumentParser(
        description="Check RM530 5G signal quality"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    # Check root access for modem communication
    if os.geteuid() != 0:
        if RICH_AVAILABLE:
            console.print("[bold red]✗[/bold red] This command must be run as root (sudo) to access modem")
        else:
            print("✗ This command must be run as root (sudo) to access modem")
        sys.exit(1)
    
    try:
        manager = RM530Manager()
        signal = manager.signal_quality()
        
        if args.json:
            import json
            output = {
                "rssi": signal.rssi,
                "rsrp": signal.rsrp,
                "rsrq": signal.rsrq,
                "sinr": signal.sinr,
                "network_type": signal.network_type,
            }
            print(json.dumps(output, indent=2))
        else:
            if RICH_AVAILABLE:
                # Create signal quality table
                table = Table(title="RM530 5G Signal Quality", box=box.ROUNDED)
                table.add_column("Metric", style="cyan", no_wrap=True)
                table.add_column("Value", style="green")
                table.add_column("Quality", style="yellow")
                
                if signal.network_type:
                    table.add_row("Network Type", signal.network_type, "")
                
                if signal.rssi is not None:
                    quality, color = get_signal_quality_label(signal.rssi)
                    quality_text = f"[{color}]{quality}[/{color}]"
                    table.add_row("RSSI", f"{signal.rssi} dBm", quality_text)
                
                if signal.rsrp is not None:
                    table.add_row("RSRP", f"{signal.rsrp} dBm", "")
                
                if signal.rsrq is not None:
                    table.add_row("RSRQ", f"{signal.rsrq} dB", "")
                
                if signal.sinr is not None:
                    table.add_row("SINR", f"{signal.sinr} dB", "")
                
                if not any([signal.rssi, signal.rsrp, signal.rsrq, signal.sinr]):
                    table.add_row("Status", "[dim]No signal data available[/dim]", "")
                
                console.print(table)
                console.print()
            else:
                # Fallback to plain text
                print("=" * 60)
                print("RM530 5G Signal Quality")
                print("=" * 60)
                print()
                
                if signal.network_type:
                    print(f"Network Type: {signal.network_type}")
                
                if signal.rssi is not None:
                    quality, _ = get_signal_quality_label(signal.rssi)
                    print(f"RSSI: {signal.rssi} dBm ({quality})")
                
                if signal.rsrp is not None:
                    print(f"RSRP: {signal.rsrp} dBm")
                
                if signal.rsrq is not None:
                    print(f"RSRQ: {signal.rsrq} dB")
                
                if signal.sinr is not None:
                    print(f"SINR: {signal.sinr} dB")
                
                if not any([signal.rssi, signal.rsrp, signal.rsrq, signal.sinr]):
                    print("No signal data available")
                
                print()
            
    except RM530Error as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")
        else:
            print(f"✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]✗ Unexpected error:[/bold red] {str(e)}")
        else:
            print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
