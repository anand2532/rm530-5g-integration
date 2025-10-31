"""NetworkManager configuration script for RM530 5G."""

import subprocess
import sys


def configure_network(interface="usb0", connection_name="RM530-5G-ECM"):
    """
    Configure NetworkManager for ECM interface.

    Args:
        interface: Network interface name (default: usb0)
        connection_name: Connection profile name (default: RM530-5G-ECM)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if connection already exists
        result = subprocess.run(
            ["nmcli", "connection", "show", connection_name], capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"Connection '{connection_name}' already exists.")
            print(f"To activate it, run: sudo nmcli connection up {connection_name}")
            return True

        # Create new connection
        cmd = [
            "nmcli",
            "connection",
            "add",
            "type",
            "ethernet",
            "ifname",
            interface,
            "con-name",
            connection_name,
            "ipv4.method",
            "auto",
            "ipv4.route-metric",
            "100",
            "ipv4.dns",
            "8.8.8.8 1.1.1.1",
            "connection.autoconnect",
            "yes",
        ]

        subprocess.run(cmd, check=True)
        print(f"✓ NetworkManager connection '{connection_name}' created successfully.")
        print(f"  Run 'sudo nmcli connection up {connection_name}' to activate.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Error configuring NetworkManager: {e}")
        return False
    except FileNotFoundError:
        print("✗ NetworkManager (nmcli) not found. Please install NetworkManager.")
        return False


def main():
    """CLI entry point for NetworkManager configuration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Configure NetworkManager for RM530 5G ECM interface"
    )
    parser.add_argument(
        "--interface", "-i", default="usb0", help="Network interface name (default: usb0)"
    )
    parser.add_argument(
        "--name",
        "-n",
        default="RM530-5G-ECM",
        help="Connection profile name (default: RM530-5G-ECM)",
    )

    args = parser.parse_args()

    success = configure_network(args.interface, args.name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
