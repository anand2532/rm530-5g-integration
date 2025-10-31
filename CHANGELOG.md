# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.1] - 2024-11-01

### Fixed
- 🐛 Fixed setup failing when modem is already in ECM mode
- 🐛 Improved graceful handling when AT command port is not accessible
- 🐛 Better error messages when modem detection fails
- 🐛 Setup now proceeds with NetworkManager configuration even if modem not detected via AT commands
- 🐛 Added interface existence check to detect if modem is already in ECM mode

### Improved
- Better handling of modem already configured in ECM mode
- More informative warning messages during setup
- Setup is more robust for existing ECM installations
- NetworkManager configuration proceeds even when AT commands unavailable

## [4.0.0] - 2024-11-01

### Added
- 🎯 **Intelligent Modem Detection** - Comprehensive modem detection system
  - USB device enumeration via multiple methods (lsusb, usb-devices, sysfs)
  - Network interface detection for CDC/ECM interfaces
  - Multi-port scanning including /dev/ttyUSB* and /dev/ttyACM* devices
  - Better port prioritization based on modem configuration
- 🔍 **Mode Detection** - Automatic modem mode detection
  - New `ModemMode` enum (QMI, ECM, MBIM, RNDIS, UNKNOWN)
  - `get_mode()` method to query current USB mode
  - Smart mode switching only when needed
  - Prevents unnecessary modem resets when already in target mode
- 📊 **Enhanced Setup Process** - Step-by-step setup with informative messages
  - Real modem detection before configuration
  - Current mode display
  - Troubleshooting hints when modem not found
  - Better error messages with actionable suggestions
- 🛠️ **Improved Error Handling**
  - Specific error messages for different failure scenarios
  - Troubleshooting tips in error output
  - Better ModemNotFoundError handling with suggestions

### Fixed
- 🐛 Fixed modem detection issues when modem is already in ECM mode
- 🐛 Fixed "No modem found" errors after successful setup
- 🐛 Improved port scanning to find modem in various configurations
- 🐛 Better handling of CDC-ACM devices
- 🐛 Fixed missing `Table` import issue in health module

### Changed
- **Improved CLI UX** - More informative setup process
  - Step-by-step progress indicators (1/4, 2/4, etc.)
  - Detailed detection information
  - Helpful troubleshooting messages
  - Better error context

### Improved
- Better robustness when modem is in different USB modes
- Enhanced logging for debugging modem detection issues
- More comprehensive USB device enumeration
- Better handling of permission errors
- Improved signal CLI error messages

## [3.0.2] - 2024-10-31

### Changed
- Updated all references from "Waveshare RM530" to "Quectel RM530" throughout documentation and code

## [3.0.1] - 2024-10-31

### Fixed
- Fixed README description to reflect version 3.0 instead of 2.0 on PyPI

## [3.0.0] - 2024-10-31

### Added
- ✨ **Enhanced CLI with Rich** - Beautiful terminal output with progress bars and tables
  - Colored output for better visibility
  - Progress indicators for long operations
  - Formatted tables for data display
  - Graceful fallback when Rich is not installed
- 🏥 **Health Monitoring System** - Automatic connection health checks and alerts
  - New `rm530-health` CLI command
  - Background health monitoring with callbacks
  - Failure threshold detection
  - Live monitoring dashboard
  - Connection health status tracking
- 🔄 **Retry Logic Utilities** - Robust error recovery mechanisms
  - Retry decorators with exponential backoff
  - Retryable/Non-retryable error distinction
  - Configurable retry attempts and delays
- ✅ **Comprehensive Testing Framework**
  - pytest test suite with fixtures
  - Unit tests for core modules
  - Coverage reporting
  - Mock support for hardware testing
- 🚀 **CI/CD Pipeline**
  - GitHub Actions workflow
  - Automated testing on multiple Python versions (3.9, 3.10, 3.11, 3.12)
  - Automated code quality checks
  - Coverage reporting integration
- 📋 **Configuration Validation**
  - APN format validation
  - Interface name validation
  - DNS server validation
  - Baudrate validation
  - Comprehensive error messages
- 📚 **Sphinx Documentation Setup**
  - API documentation generation
  - Read the Docs theme support
  - Napoleon extension for docstrings
- 🛠️ **Code Quality Tools**
  - Pre-commit hooks for automated checks
  - Black code formatter
  - isort import sorter
  - mypy type checker
  - flake8 linter

### Changed
- **Breaking**: Python 3.9+ required (was 3.8+ in v2.0)
- Enhanced CLI commands with Rich formatting (backward compatible)
- Improved error messages with helpful suggestions
- Better code organization and structure

### Improved
- Better developer experience with testing tools
- Enhanced error recovery mechanisms
- Improved code quality enforcement
- Better documentation structure

## [2.0.0] - Previous Release

### Added
- **Unified Setup Command** - Complete setup in one command (`rm530-setup`)
- **Signal Quality Monitoring** - RSSI, RSRP, RSRQ, SINR metrics (`rm530-signal`)
- **Connection Statistics** - Real-time bandwidth and connection stats (`rm530-status`)
- **Configuration File Support** - YAML config for multiple carriers
- **RM530Manager Class** - Unified API for all operations
- **Type Hints** - Full type annotations throughout codebase
- **Structured Logging** - Professional logging system
- **Custom Exceptions** - Better error handling with helpful messages

### Changed
- **Breaking**: Python 3.8+ required (was 3.7+ in v1.0)
- New unified API structure (backward compatible with v1.0 scripts)
- Better code organization with modular structure

### Improved
- Enhanced error handling
- Improved documentation
- Better code organization

## [1.0.0] - Initial Release

### Added
- ECM mode setup
- NetworkManager configuration
- Basic verification tools
- Initial package structure

---

## Version History

- **v4.0.0** (Current) - Intelligent modem detection, mode detection, and improved UX
- **v3.0.2** - Fixed README description for PyPI
- **v3.0.0** - Major release with testing, CI/CD, health monitoring, and enhanced CLI
- **v2.0.0** - Unified setup, signal monitoring, configuration management
- **v1.0.0** - Initial release with basic ECM setup functionality

## Upgrade Guide

### Upgrading from v3.x to v4.0

**Automatic migration** - No breaking changes! Just upgrade:

```bash
pip install --upgrade rm530-5g-integration
```

**What's new:**
- Better modem detection that works in all USB modes
- Automatic mode detection before setup
- More informative setup process
- Better error messages when modem not found

**No action required** - all existing configurations and commands work as before.

### Upgrading from v2.0 to v3.0

1. **Python Version**: Ensure Python 3.9+ is installed
   ```bash
   python3 --version  # Should be 3.9 or higher
   ```

2. **Installation**: Upgrade the package
   ```bash
   pip install --upgrade rm530-5g-integration
   ```

3. **New Features Available**:
   - Health monitoring: `rm530-health --help`
   - Enhanced CLI output (requires `pip install rm530-5g-integration[rich]`)
   - Retry utilities in Python API

4. **Breaking Changes**:
   - Python 3.9+ required (from 3.8+)
   - All other features are backward compatible

### Upgrading from v1.0 to v3.0

Follow the v2.0 upgrade steps above, and also note:
- Legacy commands still work, but new unified commands are recommended
- Configuration file format remains the same
- Python API has been enhanced but remains backward compatible

