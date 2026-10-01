# 16_v15_features Example

This example demonstrates the core features of WSQLite v1.5, including:
- Access to instance attributes such as `db.db_path` and `db.soft_delete` without triggering `AttributeError`.
- Soft delete (`soft_delete=True`) and restoration (`restore()`).
- Audit mixins (`AuditMixin`) with automatic `created_at` and `updated_at` timestamps.
- Native serialization/deserialization of complex JSON fields (`Dict` and `List`).

## Key Technologies & Libraries

- **[WSQLite](file:///home/william.rodriguez/Documents/w_libraries/w_libraries/wsqlite_os/wsqlite)**: SQLite ORM engine.
- **[Pydantic v2](https://docs.pydantic.dev/)**: Model validation and serialization.

## Running the Example

```bash
PYTHONPATH=src python example.py
```
