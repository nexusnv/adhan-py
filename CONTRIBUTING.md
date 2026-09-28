# Contributing to adhan-py

Thank you for your interest in contributing! This document covers the development setup, testing, and contribution process.

## Development Setup

### Prerequisites

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Clone and Install

```bash
git clone https://github.com/nexusnv/adhan-py.git
cd adhan-py

# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Or using pip
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests with coverage
pytest

# Run without coverage
pytest --no-cov

# Run a specific test file
pytest tests/test_PrayerTimes.py

# Run with verbose output
pytest -v
```

The test suite requires `pytest-mock` for some tests. Install it with:

```bash
pip install pytest-mock
```

## Code Style

This project uses the following tools:

| Tool | Purpose | Command |
|---|---|---|
| **ruff** | Linting | `ruff check src/ tests/` |
| **black** | Formatting | `black src/ tests/` |
| **mypy** | Type checking | `mypy src` |

All are enforced in CI. Run them before submitting:

```bash
ruff check src/ tests/
black --check src/ tests/
mypy src
```

## Type Annotations

All public APIs must be fully type-annotated. The project ships a `py.typed` marker (PEP 561) so downstream type-checkers can use the annotations.

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add support for X
fix: correct Y calculation
docs: update Z
refactor: extract W into separate module
test: add coverage for V
```

## Pull Requests

1. Fork the repository and create a feature branch
2. Make your changes with tests
3. Ensure all checks pass: `ruff`, `black`, `mypy`, `pytest`
4. Open a PR with a clear description of the change

## Reporting Issues

Please include:
- Python version
- Operating system
- Minimal code snippet that reproduces the issue
- Expected vs actual behavior
