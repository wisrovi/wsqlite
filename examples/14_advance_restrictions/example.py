import os
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class User(BaseModel):
    id: Optional[int] = Field(None, description="primary autoincrement")
    # Usamos 'unique:nombre_grupo' para crear una restricción compuesta
    name: str = Field(..., description="unique:name_lastname")
    lastname: str = Field(..., description="unique:name_lastname")
    email: str


db = WSQLite(User, DB_PATH)


print("=== CREATE ===")
# Primera inserción exitosa
db.insert(User(name="John", lastname="Doe", email="john1@example.com"))
db.insert(User(name="Jane", lastname="Doe", email="jane@example.com"))
print(f"Inserted 2 users, count: {db.count()}")

print("\n=== COMPOSITE UNIQUE VIOLATION ===")
try:
    # Esto debería fallar porque John Doe ya existe (aunque el email sea diferente)
    db.insert(User(name="John", lastname="Doe", email="john2@example.com"))
    print("Error: Inserción duplicada permitida (FALLO)")
except Exception as e:
    print(f"Éxito: Se detectó la violación de la restricción compuesta: {e}")

print("\n=== READ ===")
all_users = db.get_all()
for user in all_users:
    print(f"User: {user}")
