import os
from typing import Optional
from pydantic import BaseModel, Field
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Author(BaseModel):
    id: int = Field(..., description="primary")
    name: str

class Book(BaseModel):
    id: int = Field(..., description="primary")
    title: str
    # 'references:tabla.columna' crea una FOREIGN KEY
    author_id: int = Field(..., description="references:author.id")

# IMPORTANTE: Para que SQLite valide las foreign keys, hay que activarlo
# pero la librería debería manejarlo o el usuario puede hacerlo
author_db = WSQLite(Author, DB_PATH)
book_db = WSQLite(Book, DB_PATH)

print("=== CREATE ===")
author_db.insert(Author(id=1, name="Alice"))
book_db.insert(Book(id=1, title="Libro de Alice", author_id=1))
print("Registros insertados correctamente.")

print("\n=== FOREIGN KEY VIOLATION ===")
try:
    # Esto debería fallar si habilitamos foreign keys en SQLite
    # Por defecto SQLite suele tenerlos desactivados por conexión
    # Vamos a ver si el esquema se creó bien
    book_db.insert(Book(id=2, title="Libro Huérfano", author_id=99))
    print("Nota: Inserción permitida (SQLite requiere 'PRAGMA foreign_keys = ON' para validar)")
except Exception as e:
    print(f"Error detectado: {e}")

all_books = book_db.get_all()
for book in all_books:
    print(f"Book: {book}")
