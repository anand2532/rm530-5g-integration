# Release Instructions for v4.0.0

## Pre-Release Checklist

✅ Version updated to 4.0.0 in:
- `rm530_5g_integration/__init__.py`
- `pyproject.toml`

✅ CHANGELOG updated with v4.0.0 release notes

✅ README updated with new features

✅ Package builds successfully

✅ Twine check passed

## Publishing to PyPI

### Step 1: Upload to TestPyPI (Recommended First)

```bash
# Upload to TestPyPI for testing
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Or if you have credentials set:
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-testpypi-token>
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

After uploading to TestPyPI, verify installation:
```bash
pip install --index-url https://test.pypi.org/simple/ rm530-5g-integration==4.0.0
```

### Step 2: Upload to Production PyPI

#### Option A: Using Environment Variables

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-production-token>
./publish.sh
```

#### Option B: Using Interactive Mode

```bash
python3 -m twine upload dist/*
```

You'll be prompted for username and password.

#### Option C: Using publish.sh Script

```bash
chmod +x publish.sh
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-production-token>
./publish.sh
```

### Step 3: Verify Release

1. Check PyPI package page: https://pypi.org/project/rm530-5g-integration/4.0.0/
2. Test installation: `pip install rm530-5g-integration==4.0.0`
3. Verify version: `python3 -c "import rm530_5g_integration; print(rm530_5g_integration.__version__)"`

### Step 4: Create GitHub Release (Optional)

```bash
git add .
git commit -m "Release v4.0.0 - Intelligent modem detection and mode detection"
git tag -a v4.0.0 -m "Release v4.0.0: Intelligent modem detection and mode detection

- Added ModemMode enum for USB mode detection
- Implemented intelligent modem detection across all USB modes
- Added get_mode() to check current modem state
- Enhanced setup process with step-by-step feedback
- Improved error handling with troubleshooting tips
- Fixed modem detection issues in ECM mode
- Better USB device enumeration
- More robust port scanning

See CHANGELOG.md for full details."
git push origin main
git push origin v4.0.0
```

## What's New in v4.0.0

🎯 **Intelligent Modem Detection**
- USB device enumeration via multiple methods
- Network interface detection
- Multi-port scanning including /dev/ttyUSB* and /dev/ttyACM*
- Better port prioritization

🔍 **Mode Detection**
- New `ModemMode` enum (QMI, ECM, MBIM, RNDIS, UNKNOWN)
- `get_mode()` method to query current USB mode
- Smart mode switching only when needed
- Prevents unnecessary modem resets

📊 **Enhanced Setup Process**
- Real modem detection before configuration
- Current mode display
- Troubleshooting hints when modem not found
- Better error messages with actionable suggestions

🛠️ **Improved Error Handling**
- Specific error messages for different failure scenarios
- Troubleshooting tips in error output
- Better ModemNotFoundError handling

## Files Created for Release

- `dist/rm530_5g_integration-4.0.0-py3-none-any.whl` (62KB)
- `dist/rm530_5g_integration-4.0.0.tar.gz` (50KB)

## Testing the Release

After publishing, test from a clean environment:

```bash
# Create a clean virtual environment
python3 -m venv test_release
source test_release/bin/activate

# Install the package
pip install rm530-5g-integration==4.0.0

# Verify it works
python3 -c "
from rm530_5g_integration import RM530Manager, Modem, ModemMode
print(f'RM530 5G Integration v{__import__(\"rm530_5g_integration\").__version__}')
print('ModemMode enum:', [m.name for m in ModemMode])
print('✅ All imports successful!')
"

# Test CLI commands
rm530-status --help
rm530-signal --help
rm530-health --help
```

## Post-Release Tasks

1. ✅ Update version in CHANGELOG.md with actual release date
2. ✅ Monitor PyPI for download statistics
3. ✅ Watch for user feedback/issues
4. ✅ Prepare v4.0.1 patch release if needed

