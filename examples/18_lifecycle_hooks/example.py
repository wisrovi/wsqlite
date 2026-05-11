import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class User(BaseModel):
    id: int
    username: str
    status: str = "active"

    # Hook que se ejecuta antes de guardar (insert/update)
    def pre_save(self):
        print(f"  [Hook] Normalizing username: {self.username}")
        self.username = self.username.lower().strip()

    # Hook que se ejecuta después de guardar
    def post_save(self):
        print(f"  [Hook] User '{self.username}' has been synchronized with database.")

db = WSQLite(User, DB_PATH)

print("=== INSERT WITH HOOKS ===")
u = User(id=1, username="  JohnDoe  ")
db.insert(u)

print("\n=== READ VERIFICATION ===")
saved = db.get_by_field(id=1)[0]
print(f"Username in DB: '{saved.username}' (should be 'johndoe')")

os.remove(DB_PATH)
print("\nDone!")
