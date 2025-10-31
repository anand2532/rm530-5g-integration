# Project Structure

This document describes the organization and structure of the rm530-5g-integration project.

## Repository Structure

```
rm530-5g-integration/
├── .github/                    # GitHub configuration
│   ├── workflows/              # GitHub Actions workflows
│   │   └── ci.yml             # CI/CD pipeline
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                       # Project documentation
│   ├── releases/              # Release notes and version plans
│   ├── PUBLISH.md             # Publishing guide
│   ├── QUICK-PUBLISH.md       # Quick publish reference
│   ├── conf.py                # Sphinx configuration
│   ├── index.rst              # Sphinx index
│   ├── api.rst                # API reference
│   └── Makefile               # Sphinx build
├── rm530_5g_integration/      # Main package
│   ├── cli/                   # CLI commands
│   │   ├── setup.py           # Setup command
│   │   ├── status.py          # Status command
│   │   ├── signal.py          # Signal command
│   │   └── health.py          # Health monitoring (v3.0)
│   ├── core/                  # Core functionality
│   │   ├── manager.py         # Main manager class
│   │   ├── modem.py           # Modem communication
│   │   ├── network.py         # NetworkManager integration
│   │   └── health.py          # Health monitoring (v3.0)
│   ├── config/                # Configuration management
│   │   ├── loader.py          # Config loading
│   │   ├── validator.py       # Config validation (v3.0)
│   │   └── defaults.py        # Default settings
│   ├── monitoring/            # Monitoring modules
│   │   ├── signal.py          # Signal quality
│   │   └── stats.py           # Connection statistics
│   ├── utils/                 # Utilities
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── logging.py         # Logging utilities
│   │   └── retry.py           # Retry logic (v3.0)
│   ├── scripts/               # Legacy scripts (backward compat)
│   ├── docs/                  # Package documentation
│   ├── reference/             # Reference materials
│   └── legacy/                # Legacy documentation
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   └── conftest.py            # Test fixtures
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Contribution guidelines
├── README.md                  # Main documentation
├── LICENSE                    # MIT License
├── pyproject.toml             # Project configuration
├── pytest.ini                 # Pytest configuration
├── .pre-commit-config.yaml    # Pre-commit hooks
├── .gitignore                 # Git ignore rules
└── publish.sh                 # Publishing script
```

## Package Organization

### Core Modules (`rm530_5g_integration/core/`)

- **manager.py** - `RM530Manager` class providing unified API
- **modem.py** - `Modem` class for AT command communication
- **network.py** - `NetworkManager` class for network configuration
- **health.py** - `HealthMonitor` class for connection health monitoring

### CLI Commands (`rm530_5g_integration/cli/`)

- **setup.py** - Unified setup command (`rm530-setup`)
- **status.py** - Status command (`rm530-status`)
- **signal.py** - Signal quality command (`rm530-signal`)
- **health.py** - Health monitoring command (`rm530-health`)

### Configuration (`rm530_5g_integration/config/`)

- **loader.py** - Configuration file loading
- **validator.py** - Configuration validation
- **defaults.py** - Default configuration values

### Utilities (`rm530_5g_integration/utils/`)

- **exceptions.py** - Custom exception classes
- **logging.py** - Logging utilities
- **retry.py** - Retry logic decorators

### Monitoring (`rm530_5g_integration/monitoring/`)

- **signal.py** - Signal quality metrics
- **stats.py** - Connection statistics

## Documentation Organization

### Project Documentation (Root)

- **README.md** - Main project documentation
- **CHANGELOG.md** - Version history and upgrade guides
- **CONTRIBUTING.md** - Contribution guidelines
- **PROJECT-STRUCTURE.md** - This file

### Project Documentation (`docs/`)

- **releases/** - Release notes and version plans
- **PUBLISH.md** - Publishing guide
- **QUICK-PUBLISH.md** - Quick publishing reference
- Sphinx documentation configuration files

### Package Documentation (`rm530_5g_integration/docs/`)

- User guides and setup documentation
- ECM integration guide
- Verification guides

### Reference (`rm530_5g_integration/reference/`)

- AT command reference
- Troubleshooting guide

### Legacy (`rm530_5g_integration/legacy/`)

- Legacy documentation for v1.0
- Migration guides

## Testing Structure (`tests/`)

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests
│   ├── test_modem.py
│   ├── test_config.py
│   └── test_network.py (future)
└── integration/          # Integration tests (future)
```

## Development Files

- **.pre-commit-config.yaml** - Pre-commit hooks configuration
- **pytest.ini** - Pytest configuration
- **pyproject.toml** - Project metadata and tool configuration
- **.gitignore** - Git ignore patterns
- **.github/workflows/ci.yml** - CI/CD pipeline

## Build Artifacts (Excluded from Git)

- **dist/** - Built distributions
- **build/** - Build intermediate files
- ***.egg-info/** - Package metadata
- **.pytest_cache/** - Pytest cache
- **.mypy_cache/** - Type checking cache

## File Naming Conventions

- Python modules: `snake_case.py`
- Test files: `test_*.py`
- Documentation: `UPPERCASE.md` for root docs, `lowercase.md` for package docs
- Scripts: `snake_case.sh`

## Module Dependencies

```
rm530_5g_integration/
├── core/ (depends on: utils, config)
├── cli/ (depends on: core)
├── monitoring/ (depends on: core, utils)
└── utils/ (no dependencies)
```

