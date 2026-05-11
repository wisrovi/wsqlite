import os
import sqlite3
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class LegacySystemUser(BaseModel):
    id: int
    name: str

# Por defecto la tabla sería 'legacysystemuser', 
# pero podemos forzarla a 'users'
db = WSQLite(LegacySystemUser, DB_PATH, table_name="users")

print("=== TABLE NAME VERIFICATION ===")
db.insert(LegacySystemUser(id=1, name="Admin"))

# Verificar con sqlite3 directo
conn = sqlite3.connect(DB_PATH)
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
table_exists = cursor.fetchone() is not None
print(f"¿Existe tabla 'users'?: {table_exists}")

cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='legacysystemuser'")
original_exists = cursor.fetchone() is not None
print(f"¿Existe tabla 'legacysystemuser'?: {original_exists}")
conn.close()

os.remove(DB_PATH)
print("\nDone!")
