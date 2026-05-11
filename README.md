# wsqlite 🚀

**SQLite ORM using Pydantic models - Simple, Type-Safe, and High-Performance.**

<p align="center">
    <a href="https://pypi.org/project/wsqlite/">
        <img src="https://img.shields.io/pypi/v/wsqlite.svg" alt="PyPI version">
    </a>
    <a href="https://pypi.org/project/wsqlite/">
        <img src="https://img.shields.io/pypi/pyversions/wsqlite.svg" alt="Python versions">
    </a>
    <a href="https://github.com/wisrovi/wsqlite/blob/main/LICENSE">
        <img src="https://img.shields.io/pypi/l/wsqlite.svg" alt="License">
    </a>
    <a href="https://wsqlite.readthedocs.io/">
        <img src="https://img.shields.io/readthedocs/wsqlite.svg" alt="Docs">
    </a>
</p>

---

`wsqlite` is a high-level Python ORM library that provides a clean, type-safe interface for SQLite database operations. By leveraging **Pydantic v2**, it ensures data integrity and offers a modern development experience with automatic schema synchronization and full async support.

## 🌟 Key Features

- **🔗 Pydantic Integration** - Define your database schema using standard Pydantic v2 models.
- **🔄 Auto Schema Sync** - Tables are created and synchronized automatically when your models change.
- **⚡ Connection Pooling** - High-performance, thread-safe connection pool with WAL mode enabled by default.
- **📝 Intuitive CRUD** - Simple methods for `insert`, `get`, `update`, and `delete`.
- **🔍 Smart Migration** - Automatically adds new columns when detected in the model.
- **🔒 Advanced Constraints** - Native support for Primary Keys, UNIQUE (single & composite), NOT NULL, and Foreign Keys.
- **🛡️ Type Safety** - Full type hints and runtime validation powered by Pydantic.
- **⚡ Async Ready** - Full `async/await` support for high-performance applications.
- **🔨 Query Builders** - Safe, fluent API for complex queries with JOINs, GROUP BY, and more.
- **🔄 Versioned Migrations** - Robust system for schema versioning and upgrades/rollbacks.
- **🧪 Battle Tested** - 300+ tests and built-in stress testing/benchmarking tools.

## 📊 Performance at a Glance

```text
🏆 wSQLite Benchmark Results:
   - Throughput: ~5,000+ insertions/second
   - Latency: ~0.2ms average
   - Footprint: <10MB memory overhead
```

## 📦 Installation

```bash
pip install wsqlite
```

For development or benchmarking:
```bash
pip install -e ".[dev,benchmark,stress]"
```

## 🚀 Quick Start in 60 Seconds

### Define and Insert
```python
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

class User(BaseModel):
    id: Optional[int] = Field(None, description="primary autoincrement")
    name: str
    email: str = Field(..., description="unique")

# Initializing creates the table automatically
db = WSQLite(User, "app.db")

# Type-safe insertion
db.insert(User(name="John Doe", email="john@example.com"))

# Easy querying
users = db.get_all()
john = db.get_by_field(email="john@example.com")
```

### Async Operations
```python
async def main():
    await db.insert_async(User(name="Jane Doe", email="jane@example.com"))
    users = await db.get_all_async()
```

## 🎯 Advanced Functionality

### Composite Unique Constraints
```python
class Profile(BaseModel):
    username: str = Field(..., description="unique:account")
    provider: str = Field(..., description="unique:account")
# (username, provider) must be unique together
```

### Foreign Keys
```python
class Post(BaseModel):
    title: str
    author_id: int = Field(..., description="references:user.id")
```

### Powerful Query Builder
```python
from wsqlite.builders import QueryBuilder

results = (
    QueryBuilder("users")
    .select("id", "name")
    .join("orders", "users.id = orders.user_id", "LEFT")
    .where("status", "=", "active")
    .group_by("users.id")
    .having("COUNT(orders.id)", ">", 5)
    .execute(conn)
)
```

## 📁 Project Structure

- `src/wsqlite/`: Core library logic.
- `examples/`: Comprehensive usage examples (CRUD, Transactions, Relationships, etc.).
- `test/`: Full unit and integration test suite.
- `benchmark/`: Performance testing tools.

## 🧪 Testing & Quality

We maintain high standards with extensive testing:
```bash
# Run unit tests
pytest

# Run stress tests
python -m stress_test.run --scenario concurrent --records 100000
```

## 📈 Version History
- **v1.2.2** - Added Composite Uniques, Foreign Keys, and Autoid support. Fixed transaction bugs.
- **v1.2.0** - 90%+ test coverage, async connection pool.
- **v1.1.0** - Connection pooling, advanced query builder, migrations.

## 📝 License & Author

Distributed under the **MIT License**. Created with ❤️ by **William Steve Rodriguez Villamizar**.

- 📧 [wisrovi.rodriguez@gmail.com](mailto:wisrovi.rodriguez@gmail.com)
- 🔗 [GitHub](https://github.com/wisrovi) | [LinkedIn](https://www.linkedin.com/in/wisrovi/)
