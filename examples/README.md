# Examples

Usage examples demonstrating wsqlite library functionality.

## Available Examples

| Folder | Description |
|--------|-------------|
| [01_crud/](01_crud/) | Create, Read, Update, Delete operations |
| [02_new_columns/](02_new_columns/) | Adding columns to existing tables |
| [03_restrictions/](03_restrictions/) | Primary Key, UNIQUE, NOT NULL constraints |
| [04_pagination/](04_pagination/) | LIMIT/OFFSET pagination |
| [05_transactions/](05_transactions/) | Database transactions |
| [06_bulk_operations/](06_bulk_operations/) | Bulk insert/update |
| [07_logging/](07_logging/) | Logging configuration |
| [08_relationships/](08_relationships/) | Table relationships |
| [09_raw_sql/](09_raw_sql/) | Raw SQL execution |
| [10_aggregations/](10_aggregations/) | Aggregation functions |
| [11_timestamps/](11_timestamps/) | Auto timestamps |
| [12_soft_delete/](12_soft_delete/) | Soft delete pattern |
| [13_autoid/](13_autoid/) | Auto-incrementing IDs |
| [14_advance_restrictions/](14_advance_restrictions/) | Composite unique constraints |
| [15_foreign_keys/](15_foreign_keys/) | Foreign key relationships |
| [16_v15_features/](16_v15_features/) | v1.5.0 Overview: Complex types, Mixins, Soft Delete |
| [17_json_support/](17_json_support/) | JSON serialization for dict/list types |
| [18_lifecycle_hooks/](18_lifecycle_hooks/) | Lifecycle Hooks (pre_save, post_save) |
| [19_soft_delete/](19_soft_delete/) | Native Soft Delete and Restore |
| [20_mixins/](20_mixins/) | Utility Mixins (Timestamp, SoftDelete, Audit) |
| [21_custom_table_name/](21_custom_table_name/) | Custom table names for Pydantic models |
| [22_auto_indexes/](22_auto_indexes/) | Declarative automatic indexes |

## Running Examples

```bash
cd examples/01_crud
python main.py
```
