# Quick Publish Guide

## 🚀 Ready to Publish v3.0.0!

### Method 1: Using the Script (Easiest)

```bash
# 1. Set your PyPI API token
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcGl...your-token-here

# 2. Run the publish script
./publish.sh
```

### Method 2: Direct Command

```bash
# Set credentials and upload
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token

python3 -m twine upload dist/*
```

### Method 3: Using .pypirc Config File

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-your-api-token-here
```

Then run:
```bash
python3 -m twine upload dist/*
```

### Method 4: Test PyPI First (Recommended!)

```bash
# Upload to Test PyPI
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ rm530-5g-integration==3.0.0
```

## 🔑 Getting PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Enter a token name (e.g., "rm530-5g-integration")
4. Select scope: "Entire account" or "Project: rm530-5g-integration"
5. Copy the token (starts with `pypi-`)

## ✅ After Publishing

1. Verify: https://pypi.org/project/rm530-5g-integration/3.0.0/
2. Test: `pip install rm530-5g-integration==3.0.0`
3. Create git tag:
   ```bash
   git tag v3.0.0
   git push origin v3.0.0
   ```

## 📦 Current Status

✅ Package built successfully  
✅ Validation passed (twine check)  
✅ Ready to upload  
⏳ Waiting for PyPI credentials

