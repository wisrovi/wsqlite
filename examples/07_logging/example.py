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
