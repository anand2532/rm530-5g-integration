# Build Process Documentation

This document describes the build and release process for rm530-5g-integration package.

## Prerequisites

### Required Tools
- Python 3.9 or higher
- `build` package: `pip install build`
- `twine` package: `pip install twine`
- PyPI account and API token

### Optional Tools (for development)
- `pytest` - for running tests
- `black`, `isort`, `mypy`, `flake8` - for code quality checks
- `pre-commit` - for git hooks

## Build Process

### 1. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 2. Update Version

Update version in the following files:
- `rm530_5g_integration/__init__.py` - Update `__version__`
- `pyproject.toml` - Update `version` field

### 3. Build Package

```bash
python3 -m build
```

This creates:
- Source distribution: `dist/rm530_5g_integration-X.Y.Z.tar.gz`
- Wheel distribution: `dist/rm530_5g_integration-X.Y.Z-py3-none-any.whl`

### 4. Validate Package

```bash
python3 -m twine check dist/*
```

This validates:
- Package metadata
- File structure
- README rendering

### 5. Test Installation (Optional)

Test the built package locally:

```bash
pip install dist/rm530_5g_integration-X.Y.Z-py3-none-any.whl
```

Or test from source:

```bash
pip install -e .
```

## Release Process

### 1. Pre-Release Checklist

- [ ] All tests pass: `pytest tests/`
- [ ] Code formatted: `black rm530_5g_integration tests`
- [ ] Imports sorted: `isort rm530_5g_integration tests`
- [ ] Type checking: `mypy rm530_5g_integration`
- [ ] Linting: `flake8 rm530_5g_integration tests`
- [ ] README updated with version information
- [ ] Changelog updated
- [ ] Version bumped in all files

### 2. Build Package

Follow the build process above.

### 3. Publish to PyPI

#### Option A: Using Environment Variables

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
python3 -m twine upload dist/*
```

#### Option B: Using Script

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
./publish.sh
```

#### Option C: Interactive

```bash
python3 -m twine upload dist/*
# Enter credentials when prompted
```

### 4. Verify Release

- Check PyPI: https://pypi.org/project/rm530-5g-integration/
- Test installation: `pip install rm530-5g-integration==X.Y.Z`

### 5. Create Git Tag

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

### 6. Create GitHub Release (Optional)

Create a release on GitHub with:
- Release notes from CHANGELOG
- Link to PyPI package
- Highlights of new features

## Development Build

For development and testing:

```bash
# Install in editable mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Install with all optional dependencies
pip install -e ".[all]"
```

## CI/CD

The project uses GitHub Actions for automated testing and validation. See `.github/workflows/ci.yml` for details.

The CI pipeline:
- Runs on push to main/develop branches
- Runs on pull requests
- Tests on Python 3.9, 3.10, 3.11, 3.12
- Validates code quality (black, isort, flake8, mypy)
- Runs test suite
- Generates coverage reports
- Validates package build

## Version Numbering

Follows [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

Examples:
- 1.0.0 → 2.0.0: Major breaking changes
- 2.0.0 → 2.1.0: New features added
- 2.1.0 → 2.1.1: Bug fixes

## Troubleshooting

### Build Fails with License Error

If you see license-related errors, ensure `pyproject.toml` uses:
```toml
license = "MIT"  # Not {text = "MIT"}
```

And remove deprecated license classifiers.

### Upload Fails: File Already Exists

PyPI doesn't allow overwriting existing versions. Increment the version number and rebuild.

### Import Errors After Installation

Ensure all `__init__.py` files exist and package structure is correct.

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Documentation](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)

