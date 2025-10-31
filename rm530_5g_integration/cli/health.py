"""Health monitoring command."""

import sys
import argparse
import signal
import time

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.layout import Layout
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from rm530_5g_integration.core.manager import RM530Manager
from rm530_5g_integration.core.health import HealthMonitor, HealthStatus
from rm530_5g_integration.utils.logging import setup_logger

logger = setup_logger(__name__)
console = Console() if RICH_AVAILABLE else None


def create_status_table(status: HealthStatus) -> Table:
    """Create a table showing health status."""
    if not RICH_AVAILABLE:
        return None
    
    table = Table(title="Connection Health Status", box=box.ROUNDED)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    health_text = "[bold green]✓ Healthy[/bold green]" if status.is_healthy else "[bold red]✗ Unhealthy[/bold red]"
    table.add_row("Status", health_text)
    table.add_row("Last Check", status.last_check.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("Consecutive Failures", str(status.consecutive_failures))
    
    if status.connection_stats:
        stats = status.connection_stats
        table.add_row("Connected", "Yes" if stats.get("is_connected") else "No")
        if stats.get("ip_address"):
            table.add_row("IP Address", stats["ip_address"])
        if stats.get("bytes_sent") is not None:
            # Format bytes
            bytes_val = stats["bytes_sent"]
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_val < 1024.0:
                    table.add_row("Bytes Sent", f"{bytes_val:.2f} {unit}")
                    break
                bytes_val /= 1024.0
    
    if status.signal_quality:
        sig = status.signal_quality
        if sig.get("network_type"):
            table.add_row("Network Type", sig["network_type"])
        if sig.get("rssi") is not None:
            table.add_row("RSSI", f"{sig['rssi']} dBm")
    
    if status.issues:
        issues_text = "\n".join(f"• {issue}" for issue in status.issues)
        table.add_row("Issues", f"[yellow]{issues_text}[/yellow]")
    
    return table


def main():
    """CLI entry point for health monitoring."""
    parser = argparse.ArgumentParser(
        description="Monitor RM530 5G connection health"
    )
    parser.add_argument(
        "--interface", "-i",
        default="usb0",
        help="Network interface name (default: usb0)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Health check interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=3,
        help="Failure threshold before alerting (default: 3)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run health check once and exit"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Show live updating dashboard (requires rich)"
    )
    
    args = parser.parse_args()
    
    try:
        manager = RM530Manager()
        monitor = HealthMonitor(
            manager=manager,
            interface=args.interface,
            check_interval=args.interval,
            failure_threshold=args.threshold
        )
        
        if args.once:
            # Single check
            status = monitor.check_health()
            
            if RICH_AVAILABLE:
                table = create_status_table(status)
                console.print(table)
                console.print()
            else:
                print("=" * 60)
                print("Connection Health Status")
                print("=" * 60)
                print()
                print(f"Status: {'✓ Healthy' if status.is_healthy else '✗ Unhealthy'}")
                print(f"Last Check: {status.last_check}")
                print(f"Consecutive Failures: {status.consecutive_failures}")
                if status.issues:
                    print(f"Issues: {', '.join(status.issues)}")
                print()
            
            sys.exit(0 if status.is_healthy else 1)
        
        elif args.live and RICH_AVAILABLE:
            # Live monitoring dashboard
            def on_status_change(status: HealthStatus):
                """Handle status changes."""
                if not status.is_healthy:
                    console.print(f"[bold red]Alert:[/bold red] Connection unhealthy! Issues: {', '.join(status.issues)}")
            
            monitor.add_callback(on_status_change)
            monitor.start()
            
            def signal_handler(sig, frame):
                """Handle Ctrl+C."""
                monitor.stop()
                console.print("\n[bold]Monitoring stopped[/bold]")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            console.print("[bold green]Starting live health monitoring...[/bold green]")
            console.print(f"Check interval: {args.interval}s, Failure threshold: {args.threshold}")
            console.print("Press Ctrl+C to stop\n")
            
            with Live(console=console, refresh_per_second=1) as live:
                while True:
                    status = monitor.get_last_status()
                    if status:
                        table = create_status_table(status)
                        live.update(table)
                    time.sleep(1)
        
        else:
            # Background monitoring with callbacks
            def on_status_change(status: HealthStatus):
                """Handle status changes."""
                timestamp = status.last_check.strftime("%Y-%m-%d %H:%M:%S")
                
                if status.is_healthy:
                    if RICH_AVAILABLE:
                        console.print(f"[{timestamp}] [bold green]✓[/bold green] Connection healthy")
                    else:
                        print(f"[{timestamp}] ✓ Connection healthy")
                else:
                    if RICH_AVAILABLE:
                        console.print(
                            f"[{timestamp}] [bold red]✗[/bold red] Connection unhealthy "
                            f"(Failures: {status.consecutive_failures})"
                        )
                        if status.issues:
                            for issue in status.issues:
                                console.print(f"  [yellow]•[/yellow] {issue}")
                    else:
                        print(f"[{timestamp}] ✗ Connection unhealthy (Failures: {status.consecutive_failures})")
                        if status.issues:
                            for issue in status.issues:
                                print(f"  • {issue}")
                
                # Alert on threshold
                if status.consecutive_failures >= args.threshold:
                    if RICH_AVAILABLE:
                        console.print(Panel(
                            f"[bold red]ALERT:[/bold red] Connection has failed {status.consecutive_failures} "
                            f"times consecutively!\nIssues: {', '.join(status.issues)}",
                            title="Health Alert",
                            border_style="red"
                        ))
                    else:
                        print("=" * 60)
                        print(f"ALERT: Connection has failed {status.consecutive_failures} times consecutively!")
                        print(f"Issues: {', '.join(status.issues)}")
                        print("=" * 60)
            
            monitor.add_callback(on_status_change)
            monitor.start()
            
            def signal_handler(sig, frame):
                """Handle Ctrl+C."""
                monitor.stop()
                if RICH_AVAILABLE:
                    console.print("\n[bold]Monitoring stopped[/bold]")
                else:
                    print("\nMonitoring stopped")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            if RICH_AVAILABLE:
                console.print(f"[bold green]Health monitoring started[/bold green]")
                console.print(f"Check interval: {args.interval}s, Failure threshold: {args.threshold}")
                console.print("Press Ctrl+C to stop\n")
            else:
                print(f"Health monitoring started")
                print(f"Check interval: {args.interval}s, Failure threshold: {args.threshold}")
                print("Press Ctrl+C to stop\n")
            
            # Keep running
            while True:
                time.sleep(1)
            
    except KeyboardInterrupt:
        monitor.stop()
        sys.exit(0)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")
        else:
            print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

