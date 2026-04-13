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
