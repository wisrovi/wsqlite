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
