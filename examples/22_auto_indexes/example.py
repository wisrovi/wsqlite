import os
import sqlite3
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class SearchableData(BaseModel):
    id: int = Field(..., description="primary")
    # Al poner 'index' en la descripción, wsqlite crea el índice automáticamente
    category: str = Field(..., description="index")
    slug: str = Field(..., description="unique index") # Índice único

db = WSQLite(SearchableData, DB_PATH)

print("=== INDEX VERIFICATION ===")
db.insert(SearchableData(id=1, category="news", slug="v15-released"))

# Verificar índices con sqlite3
conn = sqlite3.connect(DB_PATH)
cursor = conn.execute("PRAGMA index_list('searchabledata')")
indexes = cursor.fetchall()
print("\nÍndices encontrados:")
for idx in indexes:
    print(f"- Nombre: {idx[1]}, Único: {bool(idx[2])}")
conn.close()

os.remove(DB_PATH)
print("\nDone!")
