---
project: wsqlite
title: Home
---

# wsqlite

**SQLite ORM using Pydantic models - Simple, type-safe, high-performance SQLite operations**

[![PyPI Version](https://img.shields.io/pypi/v/wsqlite.svg)](https://pypi.org/project/wsqlite/)
[![Python Versions](https://img.shields.io/pypi/pyversions/wsqlite.svg)](https://pypi.org/project/wsqlite/)
[![License](https://img.shields.io/pypi/l/wsqlite.svg)](https://github.com/wisrovi/wsqlite/blob/main/LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-79%25-brightgreen)](https://github.com/wisrovi/wsqlite)
[![Read the Docs](https://img.shields.io/readthedocs/wsqlite)](https://wsqlite.readthedocs.io/)

## Key Features

- **Pydantic Integration** - Define database schemas using Pydantic v2 models
- **Auto Table Creation** - Tables are created and synchronized automatically with model changes
- **Connection Pooling** - High-performance thread-safe connection pool with WAL mode
- **Async Support** - Full async/await for high-performance applications
- **Type Safety** - Full type hints and Pydantic validation
- **SQL Injection Prevention** - Built-in identifier validation

## Quick Start

```python
from pydantic import BaseModel
from wsqlite import WSQLite

# Define your model
class User(BaseModel):
    id: int
    name: str
    email: str

# Create database
db = WSQLite(User, "database.db")

# Insert data
db.insert(User(id=1, name="John", email="john@example.com"))

# Query data
users = db.get_all()
john = db.get_by_field(name="John")
```

## Performance

| Metric | Value |
|--------|-------|
| Operations/second | ~5,000+ |
| Average latency | ~0.2ms |
| Memory overhead | <10MB |

## Installation

```bash
pip install wsqlite
```

For development with all tools:

```bash
pip install wsqlite[dev]
```

## Why wsqlite?

- **Zero Configuration** - Works out of the box with sensible defaults
- **Type Safe** - Leverage Pydantic's validation for your data
- **Production Ready** - Connection pooling, WAL mode, and comprehensive error handling
- **Well Tested** - 300+ unit tests with 79% code coverage

## License

MIT License - See [LICENSE](https://github.com/wisrovi/wsqlite/blob/main/LICENSE) for details.

---

**Author:** William Steve Rodriguez Villamizar  
**GitHub:** [wisrovi](https://github.com/wisrovi)  
**LinkedIn:** [wisrovi-rodriguez](https://es.linkedin.com/in/wisrovi-rodriguez)
