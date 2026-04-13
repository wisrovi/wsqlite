Async Operations Tutorial
=========================

This tutorial covers async/await support in wsqlite.

Setup Async
-----------

.. code-block:: python

   import asyncio
   from pydantic import BaseModel
   from wsqlite import WSQLite

   class User(BaseModel):
       id: int
       name: str
       email: str

   db = WSQLite(User, "async.db")

Async CRUD Operations
----------------------

.. code-block:: python

   async def main():
       # Insert async
       await db.insert_async(User(id=1, name="Alice", email="alice@example.com"))

       # Get all async
       users = await db.get_all_async()
       print(f"Users: {users}")

       # Get by field async
       alice = await db.get_by_field_async(name="Alice")
       print(f"Found: {alice}")

       # Update async
       await db.update_async(1, User(id=1, name="Alice Smith", email="alice@example.com"))

       # Delete async
       await db.delete_async(1)

   asyncio.run(main())

Async Pagination
---------------

.. code-block:: python

   async def paginate():
       # Insert test data
       for i in range(50):
           await db.insert_async(User(id=i+1, name=f"User{i+1}", email=f"user{i+1}@example.com"))

       # Paginate
       page1 = await db.get_paginated_async(limit=10, offset=0)
       page2 = await db.get_page_async(page=2, per_page=10)

       # Count
       total = await db.count_async()
       print(f"Total: {total}, Page 1: {len(page1)}, Page 2: {len(page2)}")

   asyncio.run(paginate())

Async Transactions
-----------------

.. code-block:: python

   async def transaction_example():
       # Bulk insert with transaction
       users = [User(id=i, name=f"User{i}", email=f"user{i}@test.com") for i in range(100)]
       await db.insert_many_async(users)

       # Transaction async
       operations = [
           ("UPDATE user SET name = ? WHERE id = ?", ("Updated", 1)),
           ("UPDATE user SET name = ? WHERE id = ?", ("Modified", 2)),
       ]
       await db.execute_transaction_async(operations)

   asyncio.run(transaction_example())

Async TableSync
---------------

.. code-block:: python

   from wsqlite import AsyncTableSync

   async def sync_example():
       sync = AsyncTableSync(User, "async.db")

       exists = await sync.table_exists_async()
       print(f"Table exists: {exists}")

       columns = await sync.get_columns_async()
       print(f"Columns: {columns}")

   asyncio.run(sync_example())