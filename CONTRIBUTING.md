# Contributing to rm530-5g-integration

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic knowledge of Python and Linux networking

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/rm530-5g-integration.git
   cd rm530-5g-integration
   ```

2. **Install in Development Mode**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set Up Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Run Tests**
   ```bash
   pytest tests/
   ```

## Development Workflow

### Code Style

We use automated tools to maintain code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking

Before committing:
```bash
black rm530_5g_integration tests
isort rm530_5g_integration tests
flake8 rm530_5g_integration tests
mypy rm530_5g_integration
```

Or use pre-commit hooks (automatically runs on commit):
```bash
pre-commit run --all-files
```

### Testing

- Write tests for new features
- Ensure all tests pass: `pytest tests/`
- Aim for >80% code coverage
- Test with mocked hardware (don't require physical modem)

### Commit Messages

Follow the format: `/path/to/file : description`

Example:
```
rm530_5g_integration/core/modem.py : Add retry logic to AT commands
```

### Pull Requests

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Update documentation if needed
6. Commit with descriptive messages
7. Push to your fork
8. Create a Pull Request

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if needed)
- [ ] No breaking changes (or clearly documented)

## Reporting Issues

### Bug Reports

Include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, package version)
- Relevant logs/error messages

### Feature Requests

Include:
- Use case description
- Proposed solution (if any)
- Alternatives considered
- Additional context

## Code Organization

```
rm530_5g_integration/
├── core/           # Core functionality (modem, network, manager)
├── cli/            # CLI commands
├── config/         # Configuration management
├── monitoring/     # Signal and statistics
├── utils/          # Utilities (logging, exceptions, retry)
└── scripts/        # Legacy scripts (backward compatibility)
```

## Testing Guidelines

### Unit Tests
- Test individual functions/methods
- Use mocks for external dependencies
- Test edge cases and error conditions

### Integration Tests
- Test complete workflows
- Mock hardware interactions
- Test configuration loading

### Example Test Structure
```python
import pytest
from unittest.mock import Mock, patch

def test_feature_name():
    """Test description."""
    # Arrange
    # Act
    # Assert
```

## Documentation

- Update docstrings for new functions/classes
- Update README.md for user-facing changes
- Update CHANGELOG.md for new features/bug fixes
- Keep code comments clear and concise

## Release Process

See [docs/BUILD-PROCESS.md](docs/BUILD-PROCESS.md) for detailed release instructions.

## Questions?

Feel free to open an issue for questions or discussions!

