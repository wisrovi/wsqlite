import os
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from wsqlite import WSQLite, AuditMixin

DB_PATH = "complex_example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Usamos AuditMixin para tener created_at, updated_at y deleted_at automáticamente
class Task(AuditMixin):
    id: Optional[int] = Field(None, description="primary autoincrement")
    title: str = Field(..., description="index") # Creamos un índice automáticamente
    # Soporte para tipos complejos
    metadata: Dict[str, str] = {}
    tags: List[str] = []
    priority: int = 1

# Activamos soft_delete
db = WSQLite(Task, DB_PATH, soft_delete=True)

print("=== CREATE CON TIPOS COMPLEJOS ===")
task = Task(
    title="Implementar v1.5",
    metadata={"env": "prod", "version": "1.5.0"},
    tags=["python", "orm", "sqlite"]
)
db.insert(task)
print(f"Task guardada con ID 1")

print("\n=== READ Y DESERIALIZACIÓN ===")
saved = db.get_by_field(id=1)[0]
print(f"Título: {saved.title}")
print(f"Metadata (dict real): {saved.metadata} -> {type(saved.metadata)}")
print(f"Tags (list real): {saved.tags} -> {type(saved.tags)}")
print(f"Creado en: {saved.created_at}")

print("\n=== SOFT DELETE EN ACCIÓN ===")
db.delete(1)
print(f"Total registros (con filtro soft delete): {db.count()}")

# Verificamos en la DB real que el registro sigue ahí
with db._pool.connection() as conn:
    row = conn.execute("SELECT * FROM task WHERE id = 1").fetchone()
    print(f"Fila en DB real: deleted_at={row['deleted_at']}")

print("\n=== RESTORE ===")
db.restore(1)
print(f"Total registros tras restore: {db.count()}")

os.remove(DB_PATH)
print("\nDone!")
