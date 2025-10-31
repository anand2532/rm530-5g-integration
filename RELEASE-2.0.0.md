# Release v2.0.0

## 🎉 Major Release - Version 2.0.0

We're excited to announce the release of rm530-5g-integration v2.0.0 with significant improvements and new features!

## ✨ New Features

### Unified Setup Command
Complete setup in a single command:
```bash
sudo rm530-setup --apn airtelgprs.com
# or with carrier config
sudo rm530-setup --carrier airtel
```

### Signal Quality Monitoring
Monitor your 5G signal quality with detailed metrics:
```bash
sudo rm530-signal
```
Shows RSSI, RSRP, RSRQ, SINR, and network type.

### Connection Statistics
Real-time connection monitoring:
```bash
rm530-status
```
Displays IP address, bandwidth usage, packet statistics, and connection status.

### Configuration File Support
Create `~/.rm530/config.yaml` for carrier profiles and settings:
```yaml
carriers:
  airtel:
    apn: airtelgprs.com
    preferred_interface: usb0
    dns: [8.8.8.8, 1.1.1.1]
```

### RM530Manager Python API
Unified Python API for all operations:
```python
from rm530_5g_integration import RM530Manager

manager = RM530Manager()
manager.setup(apn="airtelgprs.com")
status = manager.status()
signal = manager.signal_quality()
```

## 🔧 Improvements

- **Type Hints**: Full type annotations throughout codebase
- **Logging**: Structured logging system instead of print statements
- **Error Handling**: Custom exceptions with helpful error messages
- **Code Organization**: Modular architecture with clear separation
- **Documentation**: Comprehensive docstrings and updated README

## 📊 Architecture

New modular structure:
- `core/` - Core functionality (modem, network, manager)
- `config/` - Configuration management
- `monitoring/` - Signal & statistics monitoring
- `cli/` - New unified CLI commands
- `utils/` - Logging and exception utilities

## 🔄 Breaking Changes

- **Python 3.8+ required** (was 3.7+ in v1.0)
- New unified API (backward compatible with v1.0 scripts)

## 📝 Migration Guide

**Old way (v1.0):**
```bash
sudo rm530-setup-ecm airtelgprs.com
rm530-configure-network
rm530-verify
```

**New way (v2.0):**
```bash
sudo rm530-setup --apn airtelgprs.com
```

All v1.0 commands still work for backward compatibility!

## 📦 Installation

```bash
pip install rm530-5g-integration
```

## 📚 Documentation

- [README](https://github.com/anand2532/rm530-5g-integration#readme)
- [Migration Guide](https://github.com/anand2532/rm530-5g-integration#migration-from-v10)
- Full documentation included in package

## 🙏 Thank You

Thank you for using rm530-5g-integration! This release represents a significant step forward in usability and functionality.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/rm530-5g-integration/2.0.0/)
- [GitHub Repository](https://github.com/anand2532/rm530-5g-integration)
- [Issue Tracker](https://github.com/anand2532/rm530-5g-integration/issues)

---

**Ready to stream over 5G!** 📹🚀

