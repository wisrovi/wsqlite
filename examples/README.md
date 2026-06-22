# Examples

This directory contains a collection of examples that demonstrate the usage of various modules and functionalities in this project. Each subfolder corresponds to a specific module and includes example scripts to help you understand how to use that module.

## Directory Structure

The examples are organized as follows:

```
examples/
    20_mixins/
        example.py
    22_auto_indexes/
        example.py
    15_foreign_keys/
        example.py
    09_raw_sql/
        example.py
    10_aggregations/
        example.py
    01_crud/
        example.py
    16_v15_features/
        example.py
    26_complex_types/
        example.py
    02_new_columns/
        example.py
    18_lifecycle_hooks/
        example.py
    13_autoid/
        example.py
    06_bulk_operations/
        example.py
    17_json_support/
        example.py
    19_soft_delete/
        example.py
    23_wpipe/
        example.py
    04_pagination/
        example.py
    05_transactions/
        example.py
    03_restrictions/
        example.py
    11_timestamps/
        example.py
    12_soft_delete/
        example.py
    21_custom_table_name/
        example.py
    25_relationships/
        example.py
    07_logging/
        example.py
    24_wauth/
        example.py
    wsqlite/
        crupd.py
        new_columns.py
        with_restrictions.py
    08_relationships/
        example.py
    14_advance_restrictions/
        example.py
```

## How to Use

1. Navigate to the module folder of interest, e.g., `examples/module1/`.
2. Open the `README.md` in that folder to get detailed information about the examples.
3. Run the scripts directly using:
   ```bash
   python example1.py
   ```

## Modules and Examples

### 01_crud

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class User(BaseModel):
    id: int
    name: str
    email: str


db = WSQLite(User, DB_PATH)

print("=== CREATE ===")
db.insert(User(id=1, name="Alice", email="alice@example.com"))
db.insert(User(id=2, name="Bob", email="bob@example.com"))
print(f"Inserted 2 users, count: {db.count()}")

print("\n=== READ ===")
all_users = db.get_all()
print(f"All users: {all_users}")

users_by_name = db.get_by_field(name="Alice")
print(f"Users named Alice: {users_by_name}")

print("\n=== UPDATE ===")
db.update(1, User(id=1, name="Alice Updated", email="alice.new@example.com"))
print(f"Updated user 1: {db.get_by_field(id=1)}")

print("\n=== DELETE ===")
db.delete(2)
print(f"After delete, count: {db.count()}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 02_new_columns

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import Optional
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class User(BaseModel):
    id: int
    name: str
    age: int


db = WSQLite(User, DB_PATH)
db.insert(User(id=1, name="Alice", age=25))
print(f"Initial columns: {db._sync.get_columns()}")
print(f"Users: {db.get_all()}")


class UserExtended(BaseModel):
    id: int
    name: str
    age: int
    email: Optional[str] = None


db2 = WSQLite(UserExtended, DB_PATH)
print(f"After model update, columns: {db2._sync.get_columns()}")
db2.insert(UserExtended(id=2, name="Bob", age=30, email="bob@example.com"))
print(f"Users: {db2.get_all()}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 03_restrictions

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class User(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    email: Optional[str] = Field(None, description="UNIQUE")


db = WSQLite(User, DB_PATH)

print("=== INSERT VALID ===")
db.insert(User(id=1, name="Alice", email="alice@example.com"))
print(f"Count: {db.count()}")

print("\n=== UNIQUE VIOLATION ===")
try:
    db.insert(User(id=2, name="Bob", email="alice@example.com"))
except Exception as e:
    print(f"Error: {e}")

print("\n=== INSERT MORE ===")
db.insert(User(id=2, name="Bob", email="bob@example.com"))
print(f"Count: {db.count()}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 04_pagination

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class User(BaseModel):
    id: int
    name: str


db = WSQLite(User, DB_PATH)

for i in range(25):
    db.insert(User(id=i + 1, name=f"User{i + 1}"))

print("=== PAGINATION WITH LIMIT/OFFSET ===")
page1 = db.get_paginated(limit=5, offset=0)
print(f"Page 1 (offset=0): {[u.name for u in page1]}")

page2 = db.get_paginated(limit=5, offset=5)
print(f"Page 2 (offset=5): {[u.name for u in page2]}")

print("\n=== PAGINATION WITH PAGE NUMBER ===")
page1 = db.get_page(page=1, per_page=5)
print(f"Page 1: {[u.name for u in page1]}")

page3 = db.get_page(page=3, per_page=5)
print(f"Page 3: {[u.name for u in page3]}")

print("\n=== ORDERED PAGINATION ===")
ordered = db.get_paginated(limit=5, order_by="name", order_desc=False)
print(f"Ordered by name: {[u.name for u in ordered]}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 05_transactions

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class Account(BaseModel):
    id: int
    name: str
    balance: float


db = WSQLite(Account, DB_PATH)
db.insert(Account(id=1, name="Alice", balance=1000.0))
db.insert(Account(id=2, name="Bob", balance=500.0))

print("=== BEFORE TRANSFER ===")
print(f"Alice: {db.get_by_field(id=1)[0].balance}")
print(f"Bob: {db.get_by_field(id=2)[0].balance}")

print("\n=== USING execute_transaction ===")
db.execute_transaction(
    [
        ("UPDATE account SET balance = balance - 100 WHERE id = ?", (1,)),
        ("UPDATE account SET balance = balance + 100 WHERE id = ?", (2,)),
    ]
)

print(f"Alice: {db.get_by_field(id=1)[0].balance}")
print(f"Bob: {db.get_by_field(id=2)[0].balance}")

print("\n=== USING with_transaction ===")


def transfer(txn):
    txn.execute("UPDATE account SET balance = balance - 50 WHERE id = ?", (1,))
    txn.execute("UPDATE account SET balance = balance + 50 WHERE id = ?", (2,))


db.with_transaction(transfer)

print(f"Alice: {db.get_by_field(id=1)[0].balance}")
print(f"Bob: {db.get_by_field(id=2)[0].balance}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 06_bulk_operations

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class User(BaseModel):
    id: int
    name: str


db = WSQLite(User, DB_PATH)

print("=== BULK INSERT ===")
users = [User(id=i, name=f"User{i}") for i in range(1, 101)]
db.insert_many(users)
print(f"Inserted {db.count()} users")

print("\n=== BULK UPDATE ===")
updates = [(User(id=i, name=f"Updated{i}"), i) for i in range(1, 11)]
count = db.update_many(updates)
print(f"Updated {count} users")

print("\n=== BULK DELETE ===")
count = db.delete_many([1, 2, 3, 4, 5])
print(f"Deleted {count} users")
print(f"Remaining: {db.count()}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 07_logging

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class User(BaseModel):
    id: int
    name: str

db = WSQLite(User, DB_PATH)
db.insert(User(id=1, name="Alice"))
db.insert(User(id=2, name="Bob"))
print(f"Users: {db.get_all()}")
os.remove(DB_PATH)
print("Done!")
  ```



### 08_relationships

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Author(BaseModel):
    id: int
    name: str

class Book(BaseModel):
    id: int
    title: str
    author_id: int

author_db = WSQLite(Author, DB_PATH)
book_db = WSQLite(Book, DB_PATH)

author_db.insert(Author(id=1, name="Alice"))
book_db.insert(Book(id=1, title="Book 1", author_id=1))
print(f"Authors: {author_db.get_all()}")
print(f"Books: {book_db.get_all()}")
os.remove(DB_PATH)
print("Done!")
  ```



### 09_raw_sql

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from pydantic import BaseModel
from wsqlite import WSQLite
from wsqlite.core.connection import get_transaction

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class User(BaseModel):
    id: int
    name: str

db = WSQLite(User, DB_PATH)
db.insert(User(id=1, name="Alice"))

with get_transaction(DB_PATH) as txn:
    result = txn.execute("SELECT COUNT(*) FROM user", ())
    print(f"Count: {result[0][0]}")
    
os.remove(DB_PATH)
print("Done!")
  ```



### 10_aggregations

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from pydantic import BaseModel
from wsqlite import WSQLite
from wsqlite.core.connection import get_transaction

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Product(BaseModel):
    id: int
    name: str
    price: float

db = WSQLite(Product, DB_PATH)
db.insert(Product(id=1, name="Apple", price=1.5))
db.insert(Product(id=2, name="Banana", price=0.8))

with get_transaction(DB_PATH) as txn:
    result = txn.execute("SELECT SUM(price) FROM product", ())
    print(f"Sum: {result[0][0]}")
    
os.remove(DB_PATH)
print("Done!")
  ```



### 11_timestamps

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
import time
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Record(BaseModel):
    id: int = Field(..., description="primary")
    data: str
    # Usamos datetime directamente gracias a la v1.5
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Hook automático que se ejecuta antes de INSERT y UPDATE
    def pre_save(self):
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
            print(f"  [Hook] Setting created_at: {now}")
        
        self.updated_at = now
        print(f"  [Hook] Setting updated_at: {now}")

db = WSQLite(Record, DB_PATH)

print("=== INSERT ===")
rec = Record(id=1, data="Initial Data")
db.insert(rec)

# Recuperamos para ver los tiempos
saved = db.get_by_field(id=1)[0]
print(f"Saved: created={saved.created_at}, updated={saved.updated_at}")

print("\n=== UPDATE (Waiting 1s...) ===")
time.sleep(1.1)
saved.data = "Modified Data"
db.update(saved.id, saved)

# Recuperamos de nuevo
updated = db.get_by_field(id=1)[0]
print(f"Updated: created={updated.created_at}, updated={updated.updated_at}")

if updated.updated_at > updated.created_at:
    print("\n✅ Éxito: El timestamp de 'updated_at' es posterior al de 'created_at'")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 12_soft_delete

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class User(BaseModel):
    id: int
    name: str
    deleted: Optional[int] = Field(default=0)

db = WSQLite(User, DB_PATH)
db.insert(User(id=1, name="Alice"))
db.insert(User(id=2, name="Bob"))

print(f"Total: {db.count()}")
user = db.get_by_field(id=1)[0]
db.update(1, User(id=1, name=user.name, deleted=1))
print(f"After soft delete: {db.count()}")
os.remove(DB_PATH)
print("Done!")
  ```



### 13_autoid

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class User(BaseModel):
    id: Optional[int] = Field(None, description="primary autoincrement")
    name: str
    email: str


db = WSQLite(User, DB_PATH)


print("=== CREATE ===")
# Al no pasar el id, SQLite lo generará automáticamente
db.insert(User(name="Alice", email="alice@example.com"))
db.insert(User(name="Bob", email="bob@example.com"))
print(f"Inserted 2 users, count: {db.count()}")

print("\n=== READ ===")
all_users = db.get_all()
for user in all_users:
    print(f"User: {user}")
  ```



### 14_advance_restrictions

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class User(BaseModel):
    id: Optional[int] = Field(None, description="primary autoincrement")
    # Usamos 'unique:nombre_grupo' para crear una restricción compuesta
    name: str = Field(..., description="unique:name_lastname")
    lastname: str = Field(..., description="unique:name_lastname")
    email: str


db = WSQLite(User, DB_PATH)


print("=== CREATE ===")
# Primera inserción exitosa
db.insert(User(name="John", lastname="Doe", email="john1@example.com"))
db.insert(User(name="Jane", lastname="Doe", email="jane@example.com"))
print(f"Inserted 2 users, count: {db.count()}")

print("\n=== COMPOSITE UNIQUE VIOLATION ===")
try:
    # Esto debería fallar porque John Doe ya existe (aunque el email sea diferente)
    db.insert(User(name="John", lastname="Doe", email="john2@example.com"))
    print("Error: Inserción duplicada permitida (FALLO)")
except Exception as e:
    print(f"Éxito: Se detectó la violación de la restricción compuesta: {e}")

print("\n=== READ ===")
all_users = db.get_all()
for user in all_users:
    print(f"User: {user}")
  ```



### 15_foreign_keys

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Author(BaseModel):
    id: int = Field(..., description="primary")
    name: str

class Book(BaseModel):
    id: int = Field(..., description="primary")
    title: str
    # 'references:tabla.columna' crea una FOREIGN KEY
    author_id: int = Field(..., description="references:author.id")

# IMPORTANTE: Para que SQLite valide las foreign keys, hay que activarlo
# pero la librería debería manejarlo o el usuario puede hacerlo
author_db = WSQLite(Author, DB_PATH)
book_db = WSQLite(Book, DB_PATH)

print("=== CREATE ===")
author_db.insert(Author(id=1, name="Alice"))
book_db.insert(Book(id=1, title="Libro de Alice", author_id=1))
print("Registros insertados correctamente.")

print("\n=== FOREIGN KEY VIOLATION ===")
try:
    # Esto debería fallar si habilitamos foreign keys en SQLite
    # Por defecto SQLite suele tenerlos desactivados por conexión
    # Vamos a ver si el esquema se creó bien
    book_db.insert(Book(id=2, title="Libro Huérfano", author_id=99))
    print("Nota: Inserción permitida (SQLite requiere 'PRAGMA foreign_keys = ON' para validar)")
except Exception as e:
    print(f"Error detectado: {e}")

all_books = book_db.get_all()
for book in all_books:
    print(f"Book: {book}")
  ```



### 16_v15_features

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from wsqlite import WSQLite, AuditMixin

DB_PATH = "complex_example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Usamos AuditMixin para tener created_at, updated_at y deleted_at automáticamente
class Task(AuditMixin):
    id: Optional[int] = Field(None, description="primary autoincrement")
    title: str = Field(..., description="index") # Creamos un índice automáticamente
    # Soporte para tipos complejos
    metadata: Dict[str, str] = {}
    tags: List[str] = []
    priority: int = 1

# Activamos soft_delete
db = WSQLite(Task, DB_PATH, soft_delete=True)

print("=== CREATE CON TIPOS COMPLEJOS ===")
task = Task(
    title="Implementar v1.5",
    metadata={"env": "prod", "version": "1.5.0"},
    tags=["python", "orm", "sqlite"]
)
db.insert(task)
print(f"Task guardada con ID 1")

print("\n=== READ Y DESERIALIZACIÓN ===")
saved = db.get_by_field(id=1)[0]
print(f"Título: {saved.title}")
print(f"Metadata (dict real): {saved.metadata} -> {type(saved.metadata)}")
print(f"Tags (list real): {saved.tags} -> {type(saved.tags)}")
print(f"Creado en: {saved.created_at}")

print("\n=== SOFT DELETE EN ACCIÓN ===")
db.delete(1)
print(f"Total registros (con filtro soft delete): {db.count()}")

# Verificamos en la DB real que el registro sigue ahí
with db._pool.connection() as conn:
    row = conn.execute("SELECT * FROM task WHERE id = 1").fetchone()
    print(f"Fila en DB real: deleted_at={row['deleted_at']}")

print("\n=== RESTORE ===")
db.restore(1)
print(f"Total registros tras restore: {db.count()}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 17_json_support

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import Dict, List, Any
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Configuration(BaseModel):
    id: int
    name: str
    # La v1.5.0 soporta serialización automática de dict y list a JSON
    settings: Dict[str, Any]
    tags: List[str]

db = WSQLite(Configuration, DB_PATH)

print("=== INSERTING COMPLEX TYPES ===")
config = Configuration(
    id=1,
    name="Main Config",
    settings={"theme": "dark", "notifications": True, "level": 10},
    tags=["production", "critical", "web"]
)
db.insert(config)
print("Config saved successfully.")

print("\n=== READING AND AUTO-DESERIALIZING ===")
saved = db.get_by_field(id=1)[0]
print(f"Name: {saved.name}")
print(f"Settings (dict real): {saved.settings}")
print(f"Tags (list real): {saved.tags}")

# Modificar y actualizar
saved.settings["level"] = 11
db.update(1, saved)
updated = db.get_by_field(id=1)[0]
print(f"Updated Settings: {updated.settings}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 18_lifecycle_hooks

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class User(BaseModel):
    id: int
    username: str
    status: str = "active"

    # Hook que se ejecuta antes de guardar (insert/update)
    def pre_save(self):
        print(f"  [Hook] Normalizing username: {self.username}")
        self.username = self.username.lower().strip()

    # Hook que se ejecuta después de guardar
    def post_save(self):
        print(f"  [Hook] User '{self.username}' has been synchronized with database.")

db = WSQLite(User, DB_PATH)

print("=== INSERT WITH HOOKS ===")
u = User(id=1, username="  JohnDoe  ")
db.insert(u)

print("\n=== READ VERIFICATION ===")
saved = db.get_by_field(id=1)[0]
print(f"Username in DB: '{saved.username}' (should be 'johndoe')")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 19_soft_delete

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Product(BaseModel):
    id: int
    name: str
    price: float
    # El campo de soft delete debe existir en el modelo
    deleted_at: Optional[datetime] = None

# Activamos soft_delete=True en el repositorio
db = WSQLite(Product, DB_PATH, soft_delete=True)

print("=== SETUP ===")
db.insert(Product(id=1, name="Laptop", price=1200.0))
db.insert(Product(id=2, name="Mouse", price=25.0))
print(f"Total products: {db.count()}")

print("\n=== SOFT DELETING ID 1 ===")
db.delete(1)
# count() y get_all() filtran automáticamente registros con deleted_at IS NULL
print(f"Total products (after delete): {db.count()}")
print(f"Products in list: {db.get_all()}")

print("\n=== RESTORING ID 1 ===")
db.restore(1)
print(f"Total products (after restore): {db.count()}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 20_mixins

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite, AuditMixin

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# AuditMixin añade automáticamente:
# - created_at: datetime
# - updated_at: datetime
# - deleted_at: Optional[datetime]
# - Hooks para actualizar tiempos automáticamente
class Article(AuditMixin):
    id: Optional[int] = Field(None, description="primary autoincrement")
    title: str
    content: str

# Importante: activar soft_delete=True si usas AuditMixin para el filtrado automático
db = WSQLite(Article, DB_PATH, soft_delete=True)

print("=== CREATE WITH MIXIN ===")
art = Article(title="v1.5 Released", content="Many new features added.")
db.insert(art)
print(f"Article created.")

print("\n=== READ AUDIT FIELDS ===")
saved = db.get_all()[0]
print(f"Created: {saved.created_at}")
print(f"Updated: {saved.updated_at}")

print("\n=== UPDATE AUTO-TIMESTAMP ===")
saved.title = "v1.5.0 Mega Release"
db.update(saved.id, saved)
updated = db.get_all()[0]
print(f"New Updated At: {updated.updated_at}")

os.remove(DB_PATH)
print("\nDone!")
  ```



### 21_custom_table_name

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
import sqlite3
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class LegacySystemUser(BaseModel):
    id: int
    name: str

# Por defecto la tabla sería 'legacysystemuser', 
# pero podemos forzarla a 'users'
db = WSQLite(LegacySystemUser, DB_PATH, table_name="users")

print("=== TABLE NAME VERIFICATION ===")
db.insert(LegacySystemUser(id=1, name="Admin"))

# Verificar con sqlite3 directo
conn = sqlite3.connect(DB_PATH)
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
table_exists = cursor.fetchone() is not None
print(f"¿Existe tabla 'users'?: {table_exists}")

cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='legacysystemuser'")
original_exists = cursor.fetchone() is not None
print(f"¿Existe tabla 'legacysystemuser'?: {original_exists}")
conn.close()

os.remove(DB_PATH)
print("\nDone!")
  ```



### 22_auto_indexes

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
import sqlite3
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class SearchableData(BaseModel):
    id: int = Field(..., description="primary")
    # Al poner 'index' en la descripción, wsqlite crea el índice automáticamente
    category: str = Field(..., description="index")
    slug: str = Field(..., description="unique index") # Índice único

db = WSQLite(SearchableData, DB_PATH)

print("=== INDEX VERIFICATION ===")
db.insert(SearchableData(id=1, category="news", slug="v15-released"))

# Verificar índices con sqlite3
conn = sqlite3.connect(DB_PATH)
cursor = conn.execute("PRAGMA index_list('searchabledata')")
indexes = cursor.fetchall()
print("\nÍndices encontrados:")
for idx in indexes:
    print(f"- Nombre: {idx[1]}, Único: {bool(idx[2])}")
conn.close()

os.remove(DB_PATH)
print("\nDone!")
  ```



### 23_wpipe

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import threading
import sqlite3
from typing import Any, Dict

from wsqlite import WSQLite as Wsqlite_original

# Connection pooling for performance optimization
_db_connections: Dict[str, sqlite3.Connection] = {}
_db_lock = threading.RLock()

print("=== WPIPE: Connection Pooling Example ===")
  ```



### 24_wauth

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
from wauth import WAuth
auth = WAuth(config_path="wauth.toml")

print("=== WAuth: Authentication Example ===")
  ```



### 25_relationships

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from typing import List, Optional
from pydantic import BaseModel, Field

# Modelos
class User(BaseModel):
    id: int = Field(..., description="primary")
    name: str
    posts: List["Post"] = []

class Post(BaseModel):
    id: int = Field(..., description="primary")
    title: str
    user_id: int = Field(..., description="references:user.id")
    user: Optional[User] = None

from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

db_users = WSQLite(User, DB_PATH)
db_posts = WSQLite(Post, DB_PATH)

db_users.insert(User(id=1, name="Alice"))
db_users.insert(User(id=2, name="Bob"))

db_posts.insert(Post(id=101, title="Alice's First Post", user_id=1))
db_posts.insert(Post(id=102, title="Alice's Second Post", user_id=1))
db_posts.insert(Post(id=103, title="Bob's Only Post", user_id=2))

print("=== ONE-TO-MANY: Cargar posts de un usuario ===")
user_alice = db_users.get_by_field(id=1)[0]
print(f"Usuario: {user_alice.name}")
print(f"Posts antes de cargar: {user_alice.posts}")

db_users.load_related(
    instance=user_alice,
    attribute_name="posts",
    related_db=db_posts,
    foreign_key="user_id",
    is_list=True
)

print(f"Posts después de cargar: {len(user_alice.posts)}")
for post in user_alice.posts:
    print(f"  - {post.title}")

print("")
print("=== MANY-TO-ONE: Cargar el autor de un post ===")
post_103 = db_posts.get_by_field(id=103)[0]
print(f"Post: '{post_103.title}'")
print(f"Autor antes de cargar: {post_103.user}")

db_posts.load_related(
    instance=post_103,
    attribute_name="user",
    related_db=db_users,
    foreign_key="id",
    local_key="user_id",
    is_list=False
)

print(f"Autor después de cargar: {post_103.user.name}")

os.remove(DB_PATH)
print("")
print("Done!")
  ```



### 26_complex_types

#### Description
This module demonstrates specific functionalities.


- **example.py**: Example demonstrating functionality.
```python
import os
from uuid import UUID, uuid4
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Este modelo demuestra todos los tipos complejos soportados
class Event(BaseModel):
    id: Optional[int] = Field(None, description="primary autoincrement")
    event_uuid: UUID
    event_date: date
    start_time: datetime
    value: Decimal = Field(max_digits=10, decimal_places=2)
    attendees: List[str]
    metadata: Dict[str, Any]

db = WSQLite(Event, DB_PATH)

# --- Crear una instancia con datos complejos ---
event_instance = Event(
    event_uuid=uuid4(),
    event_date=date(2026, 5, 12),
    start_time=datetime(2026, 5, 12, 14, 30, 0),
    value=Decimal("1234.56"),
    attendees=["Alice", "Bob", "Charlie"],
    metadata={"location": "Virtual", "platform": "Meet"}
)

print("=== INSERTANDO TIPOS COMPLEJOS ===")
print(f"  - UUID: {event_instance.event_uuid}")
print(f"  - Decimal: {event_instance.value}")
print(f"  - Datetime: {event_instance.start_time}")
db.insert(event_instance)
print("Evento guardado.")

print("")
print("=== LEYENDO Y VALIDANDO TIPOS ===")
saved_event = db.get_all()[0]

print(f"ID recuperado: {saved_event.id}")

# Verificar que los tipos se deserializan correctamente
assert isinstance(saved_event.event_uuid, UUID)
print(f"✅ UUID deserializado correctamente: {type(saved_event.event_uuid)}")

assert isinstance(saved_event.event_date, date)
print(f"✅ Date deserializado correctamente: {type(saved_event.event_date)}")

assert isinstance(saved_event.start_time, datetime)
print(f"✅ Datetime deserializado correctamente: {type(saved_event.start_time)}")

assert isinstance(saved_event.value, Decimal)
print(f"✅ Decimal deserializado correctamente: {type(saved_event.value)}")

assert isinstance(saved_event.attendees, list)
print(f"✅ List deserializado correctamente: {type(saved_event.attendees)}")

assert isinstance(saved_event.metadata, dict)
print(f"✅ Dict deserializado correctamente: {type(saved_event.metadata)}")

os.remove(DB_PATH)
print("")
print("Done!")
  ```



### wsqlite

#### Description
This module demonstrates specific functionalities.


- **crupd.py**: Example demonstrating functionality.
```python
from pydantic import BaseModel, Field
from wsqlite import WSQLite


# Definir el modelo sin restricciones de email
class SimpleModel2(BaseModel):
    id: int
    name: str
    age: int
    is_active: bool


# Crear la base de datos y la tabla si no existe
db = WSQLite(SimpleModel2, "database.db")

# Insertar datos
db.insert(SimpleModel2(id=1, name="Juan Pérez", age=30, is_active=True))
db.insert(SimpleModel2(id=2, name="Ana López", age=25, is_active=True))
db.insert(SimpleModel2(id=3, name="Pedro Gómez", age=40, is_active=False))

# Buscar todos los registros
print("Todos los usuarios:", db.get_all())

# Buscar por un campo específico
print("Usuarios llamados Juan:", db.get_by_field(name="Juan Pérez"))

# Buscar por múltiples filtros
print("Usuarios activos con 25 años:", db.get_by_field(age=25, is_active=True))

# Actualizar un usuario
db.update(1, SimpleModel2(id=1, name="Juan Pérez", age=31, is_active=False))
print("Usuario actualizado:", db.get_by_field(id=1))

# Eliminar un usuario
db.delete(3)
print("Usuarios después de eliminar a Pedro:", db.get_all())
  ```


- **new_columns.py**: Example demonstrating functionality.
```python
from pydantic import BaseModel, Field
from typing import Optional
from wsqlite import WSQLite


class SimpleModel4(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool


db = WSQLite(SimpleModel4, "database.db")  # Esto creará la tabla
# Insertar un nuevo usuario con el nuevo campo
db.insert(SimpleModel4(id=1, name="Ana López", age=25, is_active=True))


# === AHORA AÑADIMOS UN NUEVO CAMPO AL MODELO ===
class SimpleModel4(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool
    email: Optional[
        str
    ]  # nuevos campos no pueden tener restricciones en la base de datos (Field)


# Crear una nueva instancia con el modelo actualizado
db = WSQLite(SimpleModel4, "database.db")  # Esto actualizará la tabla

# Insertar un nuevo usuario con el nuevo campo
db.insert(
    SimpleModel4(
        id=2, name="Ana López", age=25, is_active=True, email="ana@example.com"
    )
)

# Mostrar los datos después de la actualización
print("Usuarios después de actualizar el modelo:", db.get_all())
  ```


- **with_restrictions.py**: Example demonstrating functionality.
```python
from pydantic import BaseModel, Field
from typing import Optional
from wsqlite import WSQLite


# Definir el modelo con restricciones
class SimpleModel3(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool
    email: Optional[str] = Field(None, description="UNIQUE")  # Email debe ser único


# Crear la base de datos y sincronizar con el modelo
db = WSQLite(SimpleModel3, "database.db")

# Insertar datos válidos
db.insert(
    SimpleModel3(
        id=1, name="Juan Pérez", age=30, is_active=True, email="juan@example.com"
    )
)

# Intentar insertar un usuario con el mismo email (esto fallará)
try:
    db.insert(
        SimpleModel3(
            id=2, name="Ana López", age=25, is_active=True, email="juan@example.com"
        )
    )
except Exception as e:
    print("Error al insertar usuario duplicado:", e)

# Insertar otro usuario con un email diferente (esto funcionará)
db.insert(
    SimpleModel3(
        id=3, name="Pedro Gómez", age=40, is_active=False, email="pedro@example.com"
    )
)

# Ver datos almacenados
print("Usuarios en la base de datos:", db.get_all())
  ```


