# Roadmap wsqlite

## v1.0.0 - LTS Release (Current)

- [x] Full CRUD operations (insert, get_all, get_by_field, update, delete)
- [x] Auto table creation and schema synchronization
- [x] Pydantic model integration
- [x] Constraints support (PRIMARY KEY, UNIQUE, NOT NULL)
- [x] Pagination (get_paginated, get_page)
- [x] Bulk operations (insert_many, update_many, delete_many)
- [x] Transactions (execute_transaction, with_transaction)
- [x] Full async/await support (13+ async methods)
- [x] AsyncTableSync class
- [x] QueryBuilder with SQL injection prevention
- [x] CLI tool (wsqlite CLI)
- [x] Custom exceptions hierarchy
- [x] Comprehensive test suite (50+ tests)
- [x] Connection management
- [x] Index support (create_index, drop_index, get_indexes)
- [x] Logging with loguru
- [x] Sphinx documentation

## v0.1.0 - Initial

- [x] Basic SQLite wrapper
- [x] Pydantic model support

---

## Examples available

| Folder | Functionality | Status |
|--------|---------------|--------|
| 01_crud | Create, Read, Update, Delete | ✅ |
| 02_new_columns | Add columns | ✅ |
| 03_restrictions | PK, UNIQUE, NOT NULL | ✅ |
| 04_pagination | LIMIT/OFFSET, page | ✅ |
| 05_transactions | Transactions | ✅ |
| 06_bulk_operations | insert_many, update_many | ✅ |
| 07_logging | Logging with loguru | ✅ |
| 08_relationships | Table relationships | ✅ |
| 09_raw_sql | Raw SQL execution | ✅ |
| 10_aggregations | Aggregation functions | ✅ |
| 11_timestamps | Auto timestamps | ✅ |
| 12_soft_delete | Soft delete pattern | ✅ |

---

## New features implemented

### Pagination
```python
# Using limit/offset
db.get_paginated(limit=10, offset=0, order_by="name", order_desc=True)

# Using page number
db.get_page(page=1, per_page=10)

# Count records
db.count()
```

### Transactions
```python
# Simple method
db.execute_transaction([
    ("UPDATE person SET balance = balance - 100 WHERE id = ?", (1,)),
    ("UPDATE person SET balance = balance + 100 WHERE id = ?", (2,)),
])

# Method with function
db.with_transaction(lambda txn: txn.execute("SELECT 1", ()))
```

### Bulk Operations
```python
# Insert many
db.insert_many([Person(id=1, name="Alice"), Person(id=2, name="Bob")])

# Update many
db.update_many([(Person(id=1, name="Alice"), 1), (Person(id=2, name="Bob"), 2)])

# Delete many
db.delete_many([1, 2, 3])
```

### Indexes
```python
sync = TableSync(Person, db_path)
sync.create_index(["name", "age"], unique=False)
sync.drop_index("idx_name")
indexes = sync.get_indexes()
```

### Query Builder
```python
from wsqlite import QueryBuilder

qb = (
    QueryBuilder("users")
    .where("age", ">", 18)
    .where("city", "=", "NYC")
    .order_by("name", descending=True)
    .limit(10)
    .offset(20)
)

query, values = qb.build_select()
```

### Async/Await Support

```python
import asyncio
from wsqlite import WSQLite

class User(BaseModel):
    id: int
    name: str
    email: str

async def main():
    db = WSQLite(User, "database.db")
    
    # Async CRUD operations
    await db.insert_async(User(id=1, name="John", email="john@example.com"))
    users = await db.get_all_async()
    await db.update_async(1, User(id=1, name="John", email="john@example.com"))
    await db.delete_async(1)
    
    # Async pagination
    users = await db.get_paginated_async(limit=10, offset=0)
    users = await db.get_page_async(page=1, per_page=10)
    count = await db.count_async()
    
    # Async bulk operations
    await db.insert_many_async([User(...) for i in range(100)])
    await db.update_many_async([(User(...), id) for id in ids])
    await db.delete_many_async([1, 2, 3])
    
    # Async transactions
    await db.execute_transaction_async([("INSERT...", (...)), ("UPDATE...", (...))])

asyncio.run(main())
```

### Async TableSync

```python
sync = TableSync(Person, db_path)

# Sync operations
sync.create_if_not_exists()
sync.sync_with_model()

# Async operations
await sync.create_if_not_exists_async()
await sync.sync_with_model_async()
await sync.table_exists_async()
await sync.drop_table_async()
await sync.get_columns_async()
await sync.create_index_async(["name"], unique=False)
await sync.drop_index_async("idx_name")
await sync.get_indexes_async()
```