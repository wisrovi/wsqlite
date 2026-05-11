import os
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite, AuditMixin

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# AuditMixin añade automáticamente:
# - created_at: datetime
# - updated_at: datetime
# - deleted_at: Optional[datetime]
# - Hooks para actualizar tiempos automáticamente
class Article(AuditMixin):
    id: Optional[int] = Field(None, description="primary autoincrement")
    title: str
    content: str

# Importante: activar soft_delete=True si usas AuditMixin para el filtrado automático
db = WSQLite(Article, DB_PATH, soft_delete=True)

print("=== CREATE WITH MIXIN ===")
art = Article(title="v1.5 Released", content="Many new features added.")
db.insert(art)
print(f"Article created.")

print("\n=== READ AUDIT FIELDS ===")
saved = db.get_all()[0]
print(f"Created: {saved.created_at}")
print(f"Updated: {saved.updated_at}")

print("\n=== UPDATE AUTO-TIMESTAMP ===")
saved.title = "v1.5.0 Mega Release"
db.update(saved.id, saved)
updated = db.get_all()[0]
print(f"New Updated At: {updated.updated_at}")

os.remove(DB_PATH)
print("\nDone!")
