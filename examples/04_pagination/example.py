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

for i in range(25):
    db.insert(User(id=i + 1, name=f"User{i + 1}"))

print("=== PAGINATION WITH LIMIT/OFFSET ===")
page1 = db.get_paginated(limit=5, offset=0)
print(f"Page 1 (offset=0): {[u.name for u in page1]}")

page2 = db.get_paginated(limit=5, offset=5)
print(f"Page 2 (offset=5): {[u.name for u in page2]}")

print("\n=== PAGINATION WITH PAGE NUMBER ===")
page1 = db.get_page(page=1, per_page=5)
print(f"Page 1: {[u.name for u in page1]}")

page3 = db.get_page(page=3, per_page=5)
print(f"Page 3: {[u.name for u in page3]}")

print("\n=== ORDERED PAGINATION ===")
ordered = db.get_paginated(limit=5, order_by="name", order_desc=False)
print(f"Ordered by name: {[u.name for u in ordered]}")

os.remove(DB_PATH)
print("\nDone!")
