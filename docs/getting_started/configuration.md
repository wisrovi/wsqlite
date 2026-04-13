---
title: Configuration
---

# Configuration

wsqlite provides sensible defaults out of the box, but offers extensive configuration options for production workloads.

## Basic Configuration

### Connection Pool

```python
from wsqlite import WSQLite

db = WSQLite(
    User,
    "database.db",
    pool_size=20,        # Maximum connections
    min_pool_size=2,     # Minimum connections
    use_pool=True         # Enable connection pooling
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pool_size` | int | 10 | Maximum number of connections in pool |
| `min_pool_size` | int | 2 | Minimum connections to maintain |
| `use_pool` | bool | True | Enable/disable connection pooling |

## Advanced Configuration

### Direct Connection (No Pooling)

For simple scripts or single-threaded applications:

```python
db = WSQLite(User, "database.db", use_pool=False)
```

### Custom Connection Pool

For fine-grained control:

```python
from wsqlite import ConnectionPool

pool = ConnectionPool(
    "database.db",
    min_size=5,
    max_size=50,
    timeout=60.0,
    wal_mode=True,
    busy_timeout=10000
)

db = WSQLite(User, "database.db", use_pool=True)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WSQLITE_DB_PATH` | Default database path | - |
| `WSQLITE_LOG_LEVEL` | Logging level | INFO |

## Performance Tuning

### For High Write Throughput

```python
db = WSQLite(
    User,
    "database.db",
    pool_size=50,
    min_pool_size=10
)
```

### For Read-Heavy Workloads

```python
db = WSQLite(
    User,
    "database.db",
    pool_size=20,
    min_pool_size=5
)
```

## Next Steps

- Explore [Tutorials](../tutorials/index.md) for advanced patterns
- See [API Reference](../api_reference/index.md) for complete documentation
