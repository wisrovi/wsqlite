# Source Package

Core Python package containing the wsqlite library modules.

## Structure

```
src/
└── wsqlite/           # Main package
    ├── core/         # Core database operations
    ├── builders/     # SQL query builder
    ├── exceptions/   # Custom exceptions
    ├── types/       # SQL type mapping
    └── cli/         # CLI tool
```

## Modules

- **core/** - Database connection, CRUD operations, table management
- **builders/** - Query builder for complex SQL queries
- **exceptions/** - Custom exception classes
- **types/** - Pydantic to SQLite type mapping
- **cli/** - Command-line interface implementation
