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
