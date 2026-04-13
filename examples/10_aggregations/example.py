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
