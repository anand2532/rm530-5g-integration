"""Signal quality command."""

import sys
import os
import argparse

from rm530_5g_integration.core.manager import RM530Manager
from rm530_5g_integration.utils.exceptions import RM530Error
from rm530_5g_integration.utils.logging import setup_logger

logger = setup_logger(__name__)


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
            print("=" * 60)
            print("RM530 5G Signal Quality")
            print("=" * 60)
            print()
            
            if signal.network_type:
                print(f"Network Type: {signal.network_type}")
            
            if signal.rssi is not None:
                # Signal strength interpretation
                if signal.rssi >= -70:
                    quality = "Excellent"
                elif signal.rssi >= -85:
                    quality = "Good"
                elif signal.rssi >= -100:
                    quality = "Fair"
                else:
                    quality = "Poor"
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
        print(f"✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

