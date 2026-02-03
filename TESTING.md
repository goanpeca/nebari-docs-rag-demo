# Testing Guide

## Quick Start

### Setup Pre-commit and Tests

```bash
# Run the setup script
./setup_tests.sh
```

This will:

- Install test dependencies (pytest, ruff, mypy, etc.)
- Install pre-commit hooks
- Run the test suite

## Manual Testing

### Run All Tests

```bash
conda activate nebari-rag
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_chunking.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Pre-commit Hooks

Pre-commit hooks run automatically before each git commit to ensure code quality.

### Install Hooks

```bash
pre-commit install
```

### Run Manually

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

### Hooks Included

1. **ruff**: Fast linting and formatting
2. **pydocstyle**: Docstring style checking
3. **mypy**: Static type checking
4. **bandit**: Security checks
5. **File hygiene**: Trailing whitespace, end-of-file fixes, etc.

## Test Structure

```
tests/
├── __init__.py
├── test_chunking.py      # Chunking utilities tests
├── test_agent.py         # RAG agent tests
└── test_integration.py   # End-to-end tests
```

## Writing Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test

```python
import pytest
from utils.chunking import strip_mdx_components

def test_strip_simple_component():
    """Test stripping simple JSX component."""
    content = "<Tabs>Content here</Tabs>"
    result = strip_mdx_components(content)
    assert result == "Content here"
```

## CI/CD Integration

Pre-commit hooks ensure code quality before commits. For CI/CD:

```yaml
# .github/workflows/test.yml (example)
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: conda-incubator/setup-miniconda@v2
      - run: conda env create -f environment.yml
      - run: conda activate nebari-rag && pytest tests/
```

## Troubleshooting

### Pre-commit Hook Fails

If a hook fails, fix the issue and re-commit:

```bash
# Auto-fix formatting and linting issues
ruff check --fix .
ruff format .

# Check types
mypy .

# Try committing again
git commit -m "Your message"
```

### Skipping Hooks (Emergency Only)

```bash
# Not recommended - only for emergencies
git commit --no-verify -m "Emergency fix"
```
