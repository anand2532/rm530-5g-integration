"""Verification script for RM530 5G connection."""

import re
import subprocess
import sys


def check_ecm_interface(interface_pattern="usb"):
    """Check if ECM interface is present."""
    try:
        result = subprocess.run(["ip", "link", "show"], capture_output=True, text=True, check=True)

        interfaces = re.findall(rf"\d+:\s+({interface_pattern}\d+)", result.stdout)
        if interfaces:
            print(f"✓ Found ECM interface: {', '.join(interfaces)}")
            return True
        else:
            print("✗ No ECM interface found. Is the modem in ECM mode?")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Could not check network interfaces.")
        return False


def check_network_manager(connection_name="RM530-5G-ECM"):
    """Check NetworkManager connection status."""
    try:
        result = subprocess.run(
            ["nmcli", "connection", "show", "--active"], capture_output=True, text=True, check=True
        )

        if connection_name in result.stdout:
            print(f"✓ NetworkManager connection '{connection_name}' is active.")
            return True
        else:
            print(f"✗ Connection '{connection_name}' is not active.")
            print(f"  Run: sudo nmcli connection up {connection_name}")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ Could not check NetworkManager status.")
        return None


def check_internet_connectivity():
    """Check internet connectivity."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", "8.8.8.8"], capture_output=True, check=True
        )
        print("✓ Internet connectivity: OK")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Internet connectivity: Failed")
        return False


def verify_connection():
    """Verify 5G connection is properly configured and active."""
    print("=" * 60)
    print("RM530 5G Connection Verification")
    print("=" * 60)
    print()

    checks = []

    # Check ECM interface
    checks.append(("ECM Interface", check_ecm_interface()))

    # Check NetworkManager
    nm_status = check_network_manager()
    if nm_status is not None:
        checks.append(("NetworkManager", nm_status))

    # Check internet
    checks.append(("Internet", check_internet_connectivity()))

    print()
    print("=" * 60)

    passed = sum(1 for _, status in checks if status)
    total = len(checks)

    if passed == total:
        print(f"✓ All checks passed ({passed}/{total})")
        return True
    else:
        print(f"✗ Some checks failed ({passed}/{total})")
        print("\nFor troubleshooting, see:")
        print("  rm530_5g_integration/reference/TROUBLESHOOTING.md")
        return False


def main():
    """CLI entry point for connection verification."""
    success = verify_connection()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
