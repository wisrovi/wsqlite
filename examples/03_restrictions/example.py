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
