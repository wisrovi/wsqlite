# wsqlite

**SQLite ORM using Pydantic models - simple, type-safe, high-performance SQLite operations**

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
</p>

High-level Python ORM library that provides a clean, type-safe interface for SQLite database operations using Pydantic models for schema definition.

## 🚀 Key Features

- **🔗 Pydantic Integration** - Define database schema using Pydantic v2 models
- **🔄 Auto Table Creation** - Tables created/synchronized automatically with model changes
- **⚡ Connection Pooling** - High-performance thread-safe connection pool with WAL mode
- **📝 CRUD Operations** - Simple insert, get, update, delete methods
- **🔍 Column Sync** - Automatically adds new columns when model changes
- **🔒 Constraints Support** - Primary Key, UNIQUE, NOT NULL, Foreign Keys
- **🛡️ Type Safety** - Full type hints and Pydantic validation
- **⚡ Async Support** - Full async/await for high-performance applications
- **🔨 Query Builder** - Safe query construction with SQL injection prevention
- **📊 Advanced Query Builder** - JOINs, GROUP BY, HAVING, UNION support
- **🔄 Migrations** - Version-based schema migration system
- **🧪 Stress Testing** - Built-in benchmarks and performance testing
- **💻 CLI Tool** - Command-line interface for common operations
- **🏆 Battle Tested** - Comprehensive unit and integration tests

## 📊 Performance

```
🏆 wSQLite (Pool) Benchmark Results:
   Ops/sec: ~5,000+ insertions/second
   Latency: ~0.2ms average
   Memory:  <10MB overhead
```

## 📦 Installation

```bash
pip install wsqlite
```

Development installation with dev tools:
```bash
pip install -e ".[dev]"
```

With benchmarking tools:
```bash
pip install -e ".[benchmark,stress]"
```

## 🚀 Quick Start

### Basic Usage
```python
from pydantic import BaseModel
from wsqlite import WSQLite

class User(BaseModel):
    id: int
    name: str
    email: str

# Create database - table is created automatically
db = WSQLite(User, "database.db")

# Insert data
db.insert(User(id=1, name="John", email="john@example.com"))

# Query data
users = db.get_all()
john = db.get_by_field(name="John")

# Update and delete
db.update(1, User(id=1, name="Johnny", email="johnny@example.com"))
db.delete(1)
```

### With Connection Pooling
```python
from wsqlite import WSQLite

db = WSQLite(User, "database.db", pool_size=20, min_pool_size=2)
```

### Async Operations
```python
import asyncio
from wsqlite import WSQLite

async def main():
    db = WSQLite(User, "database.db")
    await db.insert_async(User(id=1, name="John", email="john@example.com"))
    users = await db.get_all_async()

asyncio.run(main())
```

### Advanced Query Builder
```python
from wsqlite.builders import AdvancedQueryBuilder

results = (
    AdvancedQueryBuilder("users")
    .select("id", "name", "email")
    .join("orders", "users.id = orders.user_id", "LEFT")
    .where("status", "=", "active")
    .group_by("users.id")
    .having("COUNT(orders.id)", ">", 5)
    .order_by("users.name")
    .limit(100)
    .execute(conn)
)
```

### Database Migrations
```python
from wsqlite import WSQLite
from wsqlite.migrations import MigrationManager

manager = MigrationManager("app.db")

@manager.migration(1, "Create initial schema")
def m1(ctx):
    ctx.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")

manager.migrate_up()
```

## 🧪 Testing

Run tests:
```bash
pytest
```

Run stress tests:
```bash
python -m stress_test.run --scenario concurrent --records 100000 --threads 50
```

Run benchmarks:
```bash
python -m benchmark.run --all --report html
```

## 📁 Project Structure

```
wsqlite/
├── src/wsqlite/           # Main library
│   ├── __init__.py
│   ├── core/             # Core database operations
│   │   ├── connection.py # Connection management
│   │   ├── pool.py       # Connection pooling
│   │   ├── repository.py # CRUD operations
│   │   └── sync.py       # Table sync
│   ├── builders/          # Query builders
│   ├── exceptions.py      # Custom exceptions
│   ├── migrations.py      # Schema migrations
│   ├── types/            # SQL type mapping
│   ├── validators.py      # Type validation
│   └── cli/              # CLI tool
├── examples/              # Usage examples
├── test/                 # Test suite
├── stress_test/          # Stress testing
├── benchmark/            # Benchmarking
└── pyproject.toml
```

## 🎯 Advanced Features

### Connection Pool
```python
from wsqlite import ConnectionPool, WSQLite

pool = ConnectionPool("app.db", min_size=2, max_size=20)
db = WSQLite(User, "app.db", pool_size=10)

# Use pool directly
with pool.connection() as conn:
    cursor = conn.execute("SELECT * FROM users")
```

### Transactions
```python
from wsqlite import WSQLite

db = WSQLite(User, "database.db")

# Simple transaction
db.execute_transaction([
    ("INSERT INTO users VALUES (?, ?)", (1, "John")),
    ("INSERT INTO orders VALUES (?, ?)", (1, 100)),
])

# Function-based transaction
result = db.with_transaction(lambda txn: txn.execute("SELECT COUNT(*) FROM users"))
```

### Bulk Operations
```python
# Bulk insert
users = [User(id=i, name=f"User{i}", email=f"user{i}@test.com") for i in range(10000)]
db.insert_many(users)

# Bulk update
updates = [(User(id=i, name=f"Updated{i}", email=f"updated{i}@test.com"), i) for i in range(100)]
db.update_many(updates)
```

## 🔧 Configuration

### Environment Variables
- `WSQLITE_DB_PATH` - Default database path
- `WSQLITE_LOG_LEVEL` - Logging level (default: INFO)

### Pool Configuration
```python
db = WSQLite(
    User, 
    "database.db",
    pool_size=20,      # Max connections
    min_pool_size=2,   # Min connections
    use_pool=True       # Enable pooling
)
```

## 📈 Version History

- **v1.2.0** - 90%+ test coverage, async connection pool, comprehensive testing suite
- **v1.1.0** - Connection pooling, advanced query builder, migrations, stress testing
- **v1.0.0** - Initial stable release

## 🧪 Test Coverage

```bash
317 tests | 79% code coverage
```

Run with coverage:
```bash
pytest --cov=wsqlite --cov-report=term-missing
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 👤 Author

**William Steve Rodriguez Villamizar**
- Email: [wisrovi.rodriguez@gmail.com](mailto:wisrovi.rodriguez@gmail.com)
- GitHub: [wisrovi](https://github.com/wisrovi)
- LinkedIn: [wisrovi](https://www.linkedin.com/in/wisrovi/)
