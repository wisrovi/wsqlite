import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Author(BaseModel):
    id: int
    name: str

class Book(BaseModel):
    id: int
    title: str
    author_id: int

author_db = WSQLite(Author, DB_PATH)
book_db = WSQLite(Book, DB_PATH)

author_db.insert(Author(id=1, name="Alice"))
book_db.insert(Book(id=1, title="Book 1", author_id=1))
print(f"Authors: {author_db.get_all()}")
print(f"Books: {book_db.get_all()}")
os.remove(DB_PATH)
print("Done!")
