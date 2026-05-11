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
