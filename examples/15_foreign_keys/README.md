# 15_foreign_keys - Foreign Key Relationships

Demonstrates how to define and use foreign key constraints in wsqlite.

## Usage

```bash
PYTHONPATH=../../src python example.py
```

## Features Shown

- Defining foreign keys via `Field(description="references:table.column")`
- Automatic enforcement of foreign keys by the connection pool
- Handling foreign key violation errors
