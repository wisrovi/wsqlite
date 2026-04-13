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
