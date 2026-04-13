# Test Suite

Unit and integration tests for wsqlite library.

## Structure

```
test/
├── unit/           # Unit tests
│   ├── test_async.py
│   ├── test_connection.py
│   ├── test_exceptions.py
│   ├── test_query_builder.py
│   ├── test_repository.py
│   ├── test_sql_types.py
│   └── test_sync.py
├── integration/   # Integration tests
└── conftest.py    # Pytest configuration
```

## Running Tests

```bash
pytest
pytest --cov=wsqlite
pytest --cov=wsqlite --cov-report=html
```
