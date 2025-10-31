# Publishing to PyPI

## Package Built Successfully! ✅

Built files:
- `dist/rm530_5g_integration-3.0.0-py3-none-any.whl` (58K)
- `dist/rm530_5g_integration-3.0.0.tar.gz` (47K)

## Quick Publish (Recommended)

Use the provided script:

```bash
# Set your PyPI credentials
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here

# Run the publish script
./publish.sh
```

## Publishing Steps (Manual)

### Option 1: Test PyPI (Recommended first)

```bash
# Upload to Test PyPI
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ rm530-5g-integration
```

### Option 2: Production PyPI

**IMPORTANT**: Publishing to PyPI is permanent! Make sure:
- ✅ Version 3.0.0 is correct
- ✅ All tests pass
- ✅ Package validation passed (twine check)
- ✅ You have PyPI credentials ready

**Publish to Production PyPI:**

```bash
# Upload to PyPI
python3 -m twine upload dist/*
```

You will be prompted for:
- **Username**: Your PyPI username (or `__token__` for API token)
- **Password**: Your PyPI password or API token

### Using API Token (Recommended)

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Use `__token__` as username and the token as password

```bash
python3 -m twine upload dist/*
# Username: __token__
# Password: pypi-<your-token>
```

### After Publishing

1. Verify on PyPI: https://pypi.org/project/rm530-5g-integration/3.0.0/
2. Test installation: `pip install rm530-5g-integration==3.0.0`
3. Create a GitHub release tag:
   ```bash
   git tag v3.0.0
   git push origin v3.0.0
   ```

## Package Validation

✅ **twine check passed** - Package is valid and ready to publish

## Files Ready for Upload

- `dist/rm530_5g_integration-3.0.0-py3-none-any.whl`
- `dist/rm530_5g_integration-3.0.0.tar.gz`

Both files passed validation checks!

