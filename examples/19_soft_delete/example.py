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
