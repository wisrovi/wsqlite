---
title: Quick Start
---

# Quick Start

Get started with wsqlite in 5 minutes. This guide covers basic CRUD operations.

## Basic Usage

### 1. Define Your Model

```python
from pydantic import BaseModel
from wsqlite import WSQLite

class User(BaseModel):
    id: int
    name: str
    email: str
```

### 2. Create Database

```python
db = WSQLite(User, "database.db")
```

wsqlite automatically:
- Creates the database file if it doesn't exist
- Creates the table based on your Pydantic model

### 3. Insert Data

```python
# Insert a single record
db.insert(User(id=1, name="John", email="john@example.com"))

# Insert multiple records
users = [
    User(id=2, name="Alice", email="alice@example.com"),
    User(id=3, name="Bob", email="bob@example.com"),
]
db.insert_many(users)
```

### 4. Query Data

```python
# Get all records
all_users = db.get_all()

# Get by specific field
john = db.get_by_field(name="John")

# Get with pagination
page1 = db.get_page(page=1, per_page=10)

# Count records
total = db.count()
```

### 5. Update Data

```python
# Update a record
db.update(1, User(id=1, name="Johnny", email="johnny@example.com"))

# Bulk update
updates = [
    (User(id=2, name="Alice Updated", email="alice@example.com"), 2),
    (User(id=3, name="Bob Updated", email="bob@example.com"), 3),
]
db.update_many(updates)
```

### 6. Delete Data

```python
# Delete a single record
db.delete(1)

# Delete multiple records
db.delete_many([2, 3])
```

## Complete Example

```python
from pydantic import BaseModel
from wsqlite import WSQLite

class User(BaseModel):
    id: int
    name: str
    email: str

def main():
    # Create database connection
    db = WSQLite(User, "users.db")
    
    # Insert sample data
    db.insert(User(id=1, name="John", email="john@example.com"))
    db.insert(User(id=2, name="Alice", email="alice@example.com"))
    
    # Query data
    users = db.get_all()
    for user in users:
        print(f"{user.id}: {user.name} <{user.email}>")
    
    # Update data
    db.update(1, User(id=1, name="John Doe", email="johndoe@example.com"))
    
    # Delete data
    db.delete(2)
    
    # Verify changes
    print(f"Total users: {db.count()}")

if __name__ == "__main__":
    main()
```

## Next Steps

- Learn about [Configuration](configuration.md) for production optimization
- Explore [Tutorials](../tutorials/index.md) for advanced usage
