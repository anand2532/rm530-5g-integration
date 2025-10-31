# RM530 5G Integration Package

Python package for integrating Waveshare RM530 5G modem with Raspberry Pi using ECM (Ethernet Control Model) mode.

## Overview

This package provides automated tools and comprehensive documentation for setting up a Waveshare RM530 5G modem in ECM mode on Raspberry Pi. ECM mode provides native Linux integration with better stability and performance compared to QMI mode.

## Features

- ✅ **ECM Mode Setup** - Automated switching from QMI to ECM mode
- ✅ **NetworkManager Integration** - Native Linux networking support
- ✅ **Verification Tools** - Built-in verification scripts
- ✅ **Comprehensive Documentation** - Complete guides and references
- ✅ **Production Ready** - Stable and tested setup

## Installation

```bash
pip install rm530-5g-integration
```

Or from source:
```bash
git clone https://github.com/anand2532/rm530-5g-integration.git
cd rm530-5g-integration
pip install .
```

## Quick Start

### 1. Install

```bash
pip install rm530-5g-integration
```

### 2. Setup ECM Mode

```bash
sudo rm530-setup-ecm airtelgprs.com
```

Replace `airtelgprs.com` with your carrier's APN. Wait ~15 seconds for modem restart.

### 3. Configure NetworkManager

```bash
# Find the ECM interface (typically usb0)
ip link show

# Create NetworkManager connection
sudo nmcli connection add \
    type ethernet \
    ifname usb0 \
    con-name "RM530-5G-ECM" \
    ipv4.method auto \
    ipv4.route-metric 100 \
    ipv4.dns "8.8.8.8 1.1.1.1" \
    connection.autoconnect yes

# Connect
sudo nmcli connection up RM530-5G-ECM
```

### 4. Verify

```bash
ping -c 4 google.com
```

**Done!** Your 5G modem is now configured and ready to use.

## Commands

| Command | Purpose |
|---------|---------|
| `rm530-setup-ecm <apn>` | Switch modem to ECM mode |
| `rm530-configure-network [--interface usb0]` | Configure NetworkManager connection |
| `rm530-verify` | Verify 5G connection status |

## Package Contents

```
rm530-5g-integration/
├── rm530_5g_integration/
│   ├── __init__.py
│   ├── docs/              # Documentation
│   ├── reference/         # References (AT commands, etc.)
│   ├── legacy/            # Legacy QMI documentation
│   └── scripts/           # Python scripts
├── README.md
├── LICENSE
└── pyproject.toml
```

## Requirements

- Python 3.7+
- Raspberry Pi OS or Debian-based Linux
- Waveshare RM530 5G modem
- NetworkManager installed
- Root/sudo access

## Dependencies

- pyserial >= 3.5

## Usage Examples

### Python API

```python
from rm530_5g_integration.scripts.setup_ecm import switch_to_ecm_mode
from rm530_5g_integration.scripts.configure_network import configure_network
from rm530_5g_integration.scripts.verify import verify_connection

# Switch to ECM mode
success = switch_to_ecm_mode(apn="airtelgprs.com")

# Configure NetworkManager
if success:
    configure_network(interface="usb0")

# Verify connection
verify_connection()
```

## Documentation

Full documentation is included in the package:

- **Main Docs**: `rm530_5g_integration/docs/`
- **References**: `rm530_5g_integration/reference/`
- **Legacy**: `rm530_5g_integration/legacy/`

Access via Python:
```python
import rm530_5g_integration
print(rm530_5g_integration.__file__)  # Shows package location
```

## Troubleshooting

Run the verification tool to diagnose issues:
```bash
rm530-verify
```

See detailed troubleshooting guide:
- `rm530_5g_integration/reference/TROUBLESHOOTING.md`

## Features in Detail

### ECM Mode Benefits

- **Native Integration**: Uses standard Linux kernel CDC-ECM driver
- **NetworkManager Support**: Automatic management and reconnection
- **Better Performance**: Lower overhead than QMI
- **Stability**: No external dialer scripts required
- **Standard Tools**: Works with standard Linux networking tools

### Why Not QMI?

QMI mode requires external tools (waveshare-CM) and is more prone to connection issues. ECM mode provides native Linux integration with better stability.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Based on Waveshare RM530 5G modem specifications
- Compatible with Waveshare PCIe TO 4G/5G M.2 USB3.2 HAT+

## References

- [Waveshare PCIe TO 4G/5G HAT+ Wiki](https://www.waveshare.com/wiki/PCIe-TO-4G-5G-M.2-USB3.2-HAT-PLUS)
- [NetworkManager Documentation](https://networkmanager.dev/docs/)
- [Linux CDC-ECM Documentation](https://www.kernel.org/doc/html/latest/usb/cdc-ecm.html)

## Support

For issues, questions, or contributions, please use the GitHub Issues page.

---

**Ready to stream over 5G!** 📹🚀

