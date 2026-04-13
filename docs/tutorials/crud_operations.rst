CRUD Operations Tutorial
=========================

This tutorial covers the basic Create, Read, Update, and Delete operations.

Prerequisites
-------------

Ensure you have wsqlite installed:

.. code-block:: bash

   pip install wsqlite

Setup
-----

First, create a simple model and database:

.. code-block:: python

   import os
   from pydantic import BaseModel
   from wsqlite import WSQLite

   # Clean up any existing database
   if os.path.exists("tutorial.db"):
       os.remove("tutorial.db")

   class User(BaseModel):
       id: int
       name: str
       email: str

   # Create database - table created automatically
   db = WSQLite(User, "tutorial.db")

Create Operations
-----------------

Insert a single record:

.. code-block:: python

   # Insert single record
   db.insert(User(id=1, name="Alice", email="alice@example.com"))
   print("Inserted Alice")

Insert multiple records:

.. code-block:: python

   users = [
       User(id=2, name="Bob", email="bob@example.com"),
       User(id=3, name="Charlie", email="charlie@example.com"),
       User(id=4, name="Diana", email="diana@example.com"),
   ]
   db.insert_many(users)
   print(f"Inserted {len(users)} users")

Read Operations
---------------

Retrieve all records:

.. code-block:: python

   all_users = db.get_all()
   print(f"Total users: {len(all_users)}")
   for user in all_users:
       print(f"  - {user.name}: {user.email}")

Filter by specific fields:

.. code-block:: python

   # Find users by name
   alice_users = db.get_by_field(name="Alice")
   print(f"Found {len(alice_users)} users named Alice")

   # Multiple filters
   active_adults = db.get_by_field(name="Bob", email="bob@example.com")

Update Operations
-----------------

Update a specific record:

.. code-block:: python

   # Update user with id=1
   db.update(1, User(id=1, name="Alice Smith", email="alice.smith@example.com"))

   # Verify the update
   updated = db.get_by_field(id=1)
   print(f"Updated: {updated[0].name}")

Delete Operations
----------------

Delete specific records:

.. code-block:: python

   # Delete by ID
   db.delete(4)  # Delete Diana

   # Verify deletion
   remaining = db.get_all()
   print(f"Remaining users: {len(remaining)}")

   # Bulk delete
   db.delete_many([2, 3])  # Delete Bob and Charlie
   print(f"After bulk delete: {db.count()} users")

Complete Example
----------------

.. code-block:: python

   import os
   from pydantic import BaseModel
   from wsqlite import WSQLite

   class User(BaseModel):
       id: int
       name: str
       email: str

   # Clean up
   if os.path.exists("tutorial.db"):
       os.remove("tutorial.db")

   db = WSQLite(User, "tutorial.db")

   # Create
   db.insert(User(id=1, name="Alice", email="alice@example.com"))
   db.insert_many([
       User(id=2, name="Bob", email="bob@example.com"),
       User(id=3, name="Charlie", email="charlie@example.com"),
   ])

   # Read
   print(f"Total: {db.count()} users")

   # Update
   db.update(1, User(id=1, name="Alice Updated", email="alice@example.com"))

   # Delete
   db.delete(2)

   print(f"Final count: {db.count()} users")
   print("All users:", db.get_all())

   # Clean up
   os.remove("tutorial.db")

Next Steps
----------

Continue to :doc:`pagination` to learn about data pagination.