---
title: Installation
---

# Installation

## Requirements

- Python 3.9 or higher
- SQLite 3.x (included with Python)
- Pydantic 2.x

## Basic Installation

Install wsqlite from PyPI:

```bash
pip install wsqlite
```

## Development Installation

For development with testing and documentation tools:

```bash
pip install wsqlite[dev]
```

This includes:
- `pytest` - Testing framework
- `pytest-cov` - Code coverage
- `pytest-asyncio` - Async testing
- `ruff` - Linting
- `black` - Code formatting
- `mypy` - Type checking

## Optional Dependencies

### Benchmarking

```bash
pip install wsqlite[benchmark]
```

### Stress Testing

```bash
pip install wsqlite[stress]
```

## Verify Installation

Verify that wsqlite is installed correctly:

```python
import wsqlite
print(wsqlite.__version__)
```

Expected output: `1.2.0` or higher

## Virtual Environments

We strongly recommend using a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate   # Windows

# Install wsqlite
pip install wsqlite
```

## Source Installation

For the latest development version:

```bash
git clone https://github.com/wisrovi/wsqlite.git
cd wsqlite
pip install -e .
```

## Next Steps

- Continue to [Quick Start](quickstart.md) to create your first database
