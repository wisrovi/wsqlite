import os
from typing import List, Optional
from pydantic import BaseModel, Field

# Modelos
class User(BaseModel):
    id: int = Field(..., description="primary")
    name: str
    posts: List["Post"] = []

class Post(BaseModel):
    id: int = Field(..., description="primary")
    title: str
    user_id: int = Field(..., description="references:user.id")
    user: Optional[User] = None

from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

db_users = WSQLite(User, DB_PATH)
db_posts = WSQLite(Post, DB_PATH)

db_users.insert(User(id=1, name="Alice"))
db_users.insert(User(id=2, name="Bob"))

db_posts.insert(Post(id=101, title="Alice's First Post", user_id=1))
db_posts.insert(Post(id=102, title="Alice's Second Post", user_id=1))
db_posts.insert(Post(id=103, title="Bob's Only Post", user_id=2))

print("=== ONE-TO-MANY: Cargar posts de un usuario ===")
user_alice = db_users.get_by_field(id=1)[0]
print(f"Usuario: {user_alice.name}")
print(f"Posts antes de cargar: {user_alice.posts}")

db_users.load_related(
    instance=user_alice,
    attribute_name="posts",
    related_db=db_posts,
    foreign_key="user_id",
    is_list=True
)

print(f"Posts después de cargar: {len(user_alice.posts)}")
for post in user_alice.posts:
    print(f"  - {post.title}")

print("")
print("=== MANY-TO-ONE: Cargar el autor de un post ===")
post_103 = db_posts.get_by_field(id=103)[0]
print(f"Post: '{post_103.title}'")
print(f"Autor antes de cargar: {post_103.user}")

db_posts.load_related(
    instance=post_103,
    attribute_name="user",
    related_db=db_users,
    foreign_key="id",
    local_key="user_id",
    is_list=False
)

print(f"Autor después de cargar: {post_103.user.name}")

os.remove(DB_PATH)
print("")
print("Done!")
