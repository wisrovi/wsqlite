Quickstart
==========

This guide provides a quick introduction to wsqlite with practical examples.

Basic Usage
-----------

Creating a Database
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pydantic import BaseModel
   from wsqlite import WSQLite

   class User(BaseModel):
       id: int
       name: str
       email: str

   # The table is created automatically
   db = WSQLite(User, "mydatabase.db")

CRUD Operations
~~~~~~~~~~~~~~~

**Create (Insert)**

.. code-block:: python

   # Insert a single record
   db.insert(User(id=1, name="Alice", email="alice@example.com"))

   # Insert multiple records
   users = [
       User(id=2, name="Bob", email="bob@example.com"),
       User(id=3, name="Charlie", email="charlie@example.com"),
   ]
   db.insert_many(users)

**Read**

.. code-block:: python

   # Get all records
   all_users = db.get_all()

   # Filter by field
   alice = db.get_by_field(name="Alice")

   # Paginated results
   page = db.get_page(page=1, per_page=10)

**Update**

.. code-block:: python

   db.update(1, User(id=1, name="Alice Smith", email="alice.smith@example.com"))

**Delete**

.. code-block:: python

   db.delete(1)

Async Operations
----------------

For high-performance applications, use async methods:

.. code-block:: python

   import asyncio
   from wsqlite import WSQLite

   async def main():
       db = WSQLite(User, "mydatabase.db")
       
       # Async insert
       await db.insert_async(User(id=1, name="Alice", email="alice@example.com"))
       
       # Async query
       users = await db.get_all_async()

   asyncio.run(main())

Transactions
-----------

Execute multiple operations in a transaction:

.. code-block:: python

   # Method 1: execute_transaction
   db.execute_transaction([
       ("UPDATE user SET balance = balance - ? WHERE id = ?", (100, 1)),
       ("UPDATE user SET balance = balance + ? WHERE id = ?", (100, 2)),
   ])

   # Method 2: with_transaction (function callback)
   def transfer(txn):
       txn.execute("UPDATE user SET balance = balance - ? WHERE id = ?", (50, 1))
       txn.execute("UPDATE user SET balance = balance + ? WHERE id = ?", (50, 2))

   db.with_transaction(transfer)

Next Steps
----------

- Learn about :doc:`configuration` for advanced settings
- Explore :doc:`../tutorials/index` for detailed examples