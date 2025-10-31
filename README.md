# RM530 5G Integration

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/rm530-5g-integration.svg)](https://badge.fury.io/py/rm530-5g-integration)
[![CI Status](https://github.com/anand2532/rm530-5g-integration/workflows/CI/badge.svg)](https://github.com/anand2532/rm530-5g-integration/actions)

Python package for integrating Quectel RM530 5G modem with Raspberry Pi using ECM (Ethernet Control Model) mode.

## Overview

This package provides automated tools and comprehensive documentation for setting up a Quectel RM530 5G modem in ECM mode on Raspberry Pi. ECM mode provides native Linux integration with better stability and performance compared to QMI mode.

## Features

- 🚀 **One-Command Setup** - Complete modem configuration in a single command
- 🎯 **Intelligent Modem Detection** - Automatic detection across all USB modes
- 🔍 **Mode Detection** - Detects current modem mode and switches only when needed
- 📊 **Signal Quality Monitoring** - Real-time RSSI, RSRP, RSRQ, and SINR metrics
- 📈 **Connection Statistics** - Bandwidth monitoring and connection stats
- 🏥 **Health Monitoring** - Automatic connection health checks and alerts
- 🔄 **Retry Logic** - Robust error recovery with exponential backoff
- ⚙️ **Configuration Management** - YAML-based carrier profiles and settings
- ✅ **Production Ready** - Comprehensive testing and CI/CD pipeline
- 🎯 **Type Safe** - Full type annotations for better IDE support

## Installation

```bash
pip install rm530-5g-integration
```

### From Source

```bash
git clone https://github.com/anand2532/rm530-5g-integration.git
cd rm530-5g-integration
pip install .
```

### Development Installation

```bash
git clone https://github.com/anand2532/rm530-5g-integration.git
cd rm530-5g-integration
pip install -e ".[dev]"
```

## Quick Start

### Basic Setup

```bash
# Setup with APN
sudo rm530-setup --apn airtelgprs.com

# Or use carrier name (automatic APN from config)
sudo rm530-setup --carrier airtel
```

The setup command automatically:
1. Detects modem and checks current USB mode
2. Switches to ECM mode (if needed)
3. Configures NetworkManager
4. Activates the connection
5. Verifies the setup

**v4.0 Improvements**: The setup now intelligently detects your modem's current mode and only switches when necessary, preventing unnecessary resets and improving reliability.

### Check Status

```bash
# Check connection status and statistics
rm530-status

# Check signal quality
sudo rm530-signal

# Monitor connection health
rm530-health --once
```

## Commands

| Command | Description |
|---------|-------------|
| `rm530-setup [--apn APN \| --carrier NAME]` | Complete setup (ECM + NetworkManager) |
| `rm530-status [--interface usb0]` | Check connection status and statistics |
| `rm530-signal` | Display signal quality (RSSI, RSRP, RSRQ, SINR) |
| `rm530-health [--once \| --live]` | Monitor connection health |

## Configuration

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

## Python API

### Basic Usage

```python
from rm530_5g_integration import RM530Manager, Modem, ModemMode

# Initialize manager
manager = RM530Manager()

# Complete setup (automatically detects and switches mode)
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

### Advanced: Manual Mode Detection

```python
from rm530_5g_integration import Modem, ModemMode

# Check current modem mode
modem = Modem()
modem.connect()
current_mode = modem.get_mode()

if current_mode == ModemMode.ECM:
    print("Already in ECM mode!")
else:
    print(f"Current mode: {current_mode}")
    modem.switch_to_ecm_mode(apn="airtelgprs.com")
    modem.disconnect()
```

### Health Monitoring

```python
from rm530_5g_integration import HealthMonitor

monitor = HealthMonitor(
    check_interval=30,
    failure_threshold=3
)

# Single health check
status = monitor.check_health()
if status.is_healthy:
    print("Connection is healthy!")
else:
    print(f"Issues: {', '.join(status.issues)}")

# Start continuous monitoring
monitor.start()
```

## Requirements

- **Python**: 3.9+
- **OS**: Raspberry Pi OS or Debian-based Linux
- **Hardware**: Quectel RM530 5G modem
- **Software**: NetworkManager (installed by default on most Linux distributions)
- **Privileges**: Root/sudo access required for setup

## Dependencies

- `pyserial >= 3.5` - Serial communication with modem
- `pyyaml >= 6.0` - Configuration file parsing

### Optional Dependencies

- `rich >= 13.0` - Enhanced CLI output (progress bars, tables, colors)
- `sphinx >= 7.0` - Documentation generation (development)

## Project Structure

```
rm530-5g-integration/
├── rm530_5g_integration/
│   ├── core/              # Core functionality
│   │   ├── modem.py       # Modem communication
│   │   ├── network.py     # NetworkManager integration
│   │   ├── manager.py     # Main manager class
│   │   └── health.py      # Health monitoring
│   ├── config/            # Configuration management
│   ├── monitoring/        # Signal and stats monitoring
│   ├── cli/               # CLI commands
│   ├── utils/             # Utilities (logging, exceptions, retry)
│   └── scripts/           # Legacy scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── pyproject.toml
```

## Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Version history and migration guides
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines
- **[Package Documentation](rm530_5g_integration/docs/)** - Detailed guides and references

## Troubleshooting

Run the verification tool to diagnose issues:

```bash
rm530-status
```

Or check signal quality:

```bash
sudo rm530-signal
```

For detailed troubleshooting, see the [troubleshooting guide](rm530_5g_integration/reference/TROUBLESHOOTING.md).

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on Quectel RM530 5G modem specifications
- Compatible with Waveshare PCIe TO 4G/5G M.2 USB3.2 HAT+

## Support

- **Issues**: [GitHub Issues](https://github.com/anand2532/rm530-5g-integration/issues)
- **Documentation**: See the [docs](rm530_5g_integration/docs/) directory

---

**Ready to stream over 5G!** 📹🚀
