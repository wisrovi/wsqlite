Bulk Operations Tutorial
========================

This tutorial covers bulk insert, update, and delete operations.

Bulk Insert
-----------

.. code-block:: python

   from pydantic import BaseModel
   from wsqlite import WSQLite

   class User(BaseModel):
       id: int
       name: str

   db = WSQLite(User, "bulk.db")

   # Bulk insert 100 users
   users = [User(id=i, name=f"User{i}") for i in range(1, 101)]
   db.insert_many(users)
   print(f"Inserted {db.count()} users")

Bulk Update
-----------

.. code-block:: python

   # Update multiple users
   updates = [
       (User(id=i, name=f"Updated{i}"), i)
       for i in range(1, 11)
   ]
   count = db.update_many(updates)
   print(f"Updated {count} users")

Bulk Delete
-----------

.. code-block:: python

   # Delete multiple users by IDs
   ids_to_delete = list(range(1, 21))
   count = db.delete_many(ids_to_delete)
   print(f"Deleted {count} users")

Async Bulk Operations
---------------------

.. code-block:: python

   import asyncio

   async def async_bulk():
       users = [User(id=i, name=f"User{i}") for i in range(1000)]
       await db.insert_many_async(users)
       print(f"Async inserted {await db.count_async()} users")

   asyncio.run(async_bulk())