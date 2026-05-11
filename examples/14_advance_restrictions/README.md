# 14_advance_restrictions - Composite Unique Constraints

Demonstrates how to define unique constraints across multiple columns in wsqlite.

## Usage

```bash
PYTHONPATH=../../src python example.py
```

## Features Shown

- Defining composite unique constraints via `Field(description="unique:group_name")`
- Automatic creation of table-level `UNIQUE` constraints
- Handling composite unique violation errors
