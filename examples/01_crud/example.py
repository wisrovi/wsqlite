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

print(f"Connected to database file at: {db.db_path}")
assert db.db_path == DB_PATH, f"Expected db_path to be {DB_PATH}, got {db.db_path}"
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
