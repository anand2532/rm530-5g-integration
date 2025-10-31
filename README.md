# RM530 5G Integration Package v2.0

Python package for integrating Waveshare RM530 5G modem with Raspberry Pi using ECM (Ethernet Control Model) mode.

## Overview

This package provides automated tools and comprehensive documentation for setting up a Waveshare RM530 5G modem in ECM mode on Raspberry Pi. ECM mode provides native Linux integration with better stability and performance compared to QMI mode.

## 🎉 Version 2.0 Highlights

- ✨ **Unified Setup Command** - Complete setup in one command
- 📊 **Signal Quality Monitoring** - RSSI, RSRP, RSRQ, SINR metrics
- 📈 **Connection Statistics** - Real-time bandwidth and connection stats
- ⚙️ **Configuration Files** - YAML config for multiple carriers
- 🎯 **Type Hints** - Full type annotations for better IDE support
- 📝 **Structured Logging** - Professional logging system
- 🔧 **Better Error Handling** - Custom exceptions with helpful messages

## Features

- ✅ **ECM Mode Setup** - Automated switching from QMI to ECM mode
- ✅ **NetworkManager Integration** - Native Linux networking support
- ✅ **Unified Setup** - One command for complete configuration
- ✅ **Signal Monitoring** - Real-time signal quality metrics
- ✅ **Connection Statistics** - Bandwidth and connection monitoring
- ✅ **Configuration Management** - Carrier profiles and settings
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

## Quick Start (v2.0 - Recommended)

### Single Command Setup

```bash
# Setup with APN
sudo rm530-setup --apn airtelgprs.com

# Or use carrier name (automatic APN from config)
sudo rm530-setup --carrier airtel
```

That's it! The command will:
1. Switch modem to ECM mode
2. Configure NetworkManager
3. Activate the connection
4. Verify setup

### Check Status

```bash
# Check connection status
rm530-status

# Check signal quality
sudo rm530-signal
```

## Quick Start (Legacy - v1.0 style)

### Step-by-step Setup

```bash
# 1. Switch to ECM mode
sudo rm530-setup-ecm airtelgprs.com

# 2. Wait 15 seconds for modem restart, then configure NetworkManager
rm530-configure-network

# 3. Verify connection
rm530-verify
```

## Commands

### v2.0 Commands (Recommended)

| Command | Purpose |
|---------|---------|
| `rm530-setup [--apn APN \| --carrier NAME]` | Complete setup (ECM + NetworkManager) |
| `rm530-status [--interface usb0]` | Check connection status and statistics |
| `rm530-signal` | Display signal quality (RSSI, RSRP, RSRQ, SINR) |

### Legacy Commands (v1.0 - Still Supported)

| Command | Purpose |
|---------|---------|
| `rm530-setup-ecm <apn>` | Switch modem to ECM mode |
| `rm530-configure-network [--interface usb0]` | Configure NetworkManager connection |
| `rm530-verify` | Verify 5G connection status |

## Configuration File

Create `~/.rm530/config.yaml` for carrier profiles:

```yaml
carriers:
  airtel:
    apn: airtelgprs.com
    preferred_interface: usb0
    dns: [8.8.8.8, 1.1.1.1]
  jio:
    apn: jionet
    preferred_interface: usb0
    dns: [8.8.8.8, 1.1.1.1]

defaults:
  route_metric: 100
  autoconnect: true
  ipv4_method: auto
  connection_name: RM530-5G-ECM
```

Then use:
```bash
sudo rm530-setup --carrier airtel
```

## Usage Examples

### Python API (v2.0)

```python
from rm530_5g_integration import RM530Manager

# Initialize manager
manager = RM530Manager()

# Complete setup
manager.setup(apn="airtelgprs.com", carrier="airtel")

# Check status
status = manager.status()
print(f"IP Address: {status.ip_address}")
print(f"Bytes Sent: {status.bytes_sent}")

# Get signal quality
signal = manager.signal_quality()
print(f"RSSI: {signal.rssi} dBm")
print(f"Network Type: {signal.network_type}")

# Verify connection
if manager.verify():
    print("Connection is working!")
```

### Python API (Legacy)

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

## Package Structure

```
rm530-5g-integration/
├── rm530_5g_integration/
│   ├── core/              # Core functionality
│   │   ├── modem.py       # Modem communication
│   │   ├── network.py     # NetworkManager integration
│   │   └── manager.py     # Main manager class
│   ├── config/            # Configuration management
│   ├── monitoring/        # Signal and stats monitoring
│   ├── cli/               # CLI commands (v2.0)
│   ├── utils/             # Utilities (logging, exceptions)
│   ├── scripts/           # Legacy scripts (v1.0)
│   ├── docs/              # Documentation
│   ├── reference/         # References
│   └── legacy/            # Legacy documentation
├── README.md
├── LICENSE
└── pyproject.toml
```

## Requirements

- Python 3.8+ (was 3.7+ in v1.0)
- Raspberry Pi OS or Debian-based Linux
- Waveshare RM530 5G modem
- NetworkManager installed
- Root/sudo access

## Dependencies

- pyserial >= 3.5
- pyyaml >= 6.0 (for configuration files)

## Migration from v1.0

### Breaking Changes

1. **Python 3.8+ required** (was 3.7+)
2. **New unified API** - Use `RM530Manager` class instead of individual scripts
3. **New CLI commands** - `rm530-setup` replaces multiple commands

### Migration Guide

**Old way (v1.0):**
```bash
sudo rm530-setup-ecm airtelgprs.com
# wait...
rm530-configure-network
rm530-verify
```

**New way (v2.0):**
```bash
sudo rm530-setup --apn airtelgprs.com
```

**Python API:**

```python
# Old (v1.0) - still works!
from rm530_5g_integration.scripts.setup_ecm import switch_to_ecm_mode

# New (v2.0) - recommended
from rm530_5g_integration import RM530Manager
manager = RM530Manager()
manager.setup(apn="airtelgprs.com")
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
rm530-status
```

Or check signal quality:
```bash
sudo rm530-signal
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

### Signal Quality Metrics

- **RSSI**: Received Signal Strength Indicator (dBm)
- **RSRP**: Reference Signal Received Power (dBm) - 4G/5G
- **RSRQ**: Reference Signal Received Quality (dB) - 4G/5G
- **SINR**: Signal to Interference plus Noise Ratio (dB) - 4G/5G

### Connection Statistics

- Real-time bandwidth monitoring (bytes sent/received)
- Packet statistics
- Connection uptime
- IP address information

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Changelog

### Version 2.0.0

**New Features:**
- Unified setup command (`rm530-setup`)
- Signal quality monitoring (`rm530-signal`)
- Connection statistics (`rm530-status`)
- Configuration file support (YAML)
- `RM530Manager` class for unified API
- Full type hints throughout codebase
- Structured logging system
- Custom exceptions with better error messages

**Breaking Changes:**
- Python 3.8+ required (was 3.7+)
- New API structure (backward compatible with v1.0 scripts)

**Improvements:**
- Better code organization
- Enhanced error handling
- Improved documentation

### Version 1.0.0

- Initial release
- ECM mode setup
- NetworkManager configuration
- Basic verification tools

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
