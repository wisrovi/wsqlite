# 13_autoid - Auto-incrementing IDs

Demonstrates how to define and use auto-incrementing primary keys in wsqlite.

## Usage

```bash
PYTHONPATH=../../src python example.py
```

## Features Shown

- Use of `Optional[int]` for primary keys
- Defining `AUTOINCREMENT` constraint via `Field(description="...")`
- Automatic ID generation by SQLite when inserting records
