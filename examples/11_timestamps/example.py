import os
import time
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Record(BaseModel):
    id: int = Field(..., description="primary")
    data: str
    # Usamos datetime directamente gracias a la v1.5
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Hook automático que se ejecuta antes de INSERT y UPDATE
    def pre_save(self):
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
            print(f"  [Hook] Setting created_at: {now}")
        
        self.updated_at = now
        print(f"  [Hook] Setting updated_at: {now}")

db = WSQLite(Record, DB_PATH)

print("=== INSERT ===")
rec = Record(id=1, data="Initial Data")
db.insert(rec)

# Recuperamos para ver los tiempos
saved = db.get_by_field(id=1)[0]
print(f"Saved: created={saved.created_at}, updated={saved.updated_at}")

print("\n=== UPDATE (Waiting 1s...) ===")
time.sleep(1.1)
saved.data = "Modified Data"
db.update(saved.id, saved)

# Recuperamos de nuevo
updated = db.get_by_field(id=1)[0]
print(f"Updated: created={updated.created_at}, updated={updated.updated_at}")

if updated.updated_at > updated.created_at:
    print("\n✅ Éxito: El timestamp de 'updated_at' es posterior al de 'created_at'")

os.remove(DB_PATH)
print("\nDone!")
