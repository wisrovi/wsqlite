import os
from typing import Dict, List, Any
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Configuration(BaseModel):
    id: int
    name: str
    # La v1.5.0 soporta serialización automática de dict y list a JSON
    settings: Dict[str, Any]
    tags: List[str]

db = WSQLite(Configuration, DB_PATH)

print("=== INSERTING COMPLEX TYPES ===")
config = Configuration(
    id=1,
    name="Main Config",
    settings={"theme": "dark", "notifications": True, "level": 10},
    tags=["production", "critical", "web"]
)
db.insert(config)
print("Config saved successfully.")

print("\n=== READING AND AUTO-DESERIALIZING ===")
saved = db.get_by_field(id=1)[0]
print(f"Name: {saved.name}")
print(f"Settings (dict real): {saved.settings}")
print(f"Tags (list real): {saved.tags}")

# Modificar y actualizar
saved.settings["level"] = 11
db.update(1, saved)
updated = db.get_by_field(id=1)[0]
print(f"Updated Settings: {updated.settings}")

os.remove(DB_PATH)
print("\nDone!")
