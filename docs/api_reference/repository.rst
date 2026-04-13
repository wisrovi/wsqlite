WSQLite Repository
==================

The main repository class for SQLite database operations.

.. autoclass:: wsqlite.core.repository.WSQLite
   :members:
   :undoc-members:
   :show-inheritance:

Sync Methods
-----------

.. rubric:: CRUD Operations

.. csv-table::
   :header: "Method", "Description"

   "insert()", "Insert a single record"
   "get_all()", "Retrieve all records"
   "get_by_field()", "Filter records by field values"
   "update()", "Update a record by ID"
   "delete()", "Delete a record by ID"

.. rubric:: Pagination

.. csv-table::
   :header: "Method", "Description"

   "get_paginated()", "Get records with limit/offset"
   "get_page()", "Get records by page number"
   "count()", "Get total record count"

.. rubric:: Bulk Operations

.. csv-table::
   :header: "Method", "Description"

   "insert_many()", "Insert multiple records"
   "update_many()", "Update multiple records"
   "delete_many()", "Delete multiple records"

.. rubric:: Transactions

.. csv-table::
   :header: "Method", "Description"

   "execute_transaction()", "Execute operations in transaction"
   "with_transaction()", "Execute callback in transaction"

Async Methods
-------------

All sync methods have async equivalents with ``_async`` suffix:

- ``insert_async()``
- ``get_all_async()``
- ``get_by_field_async()``
- ``update_async()``
- ``delete_async()``
- ``get_paginated_async()``
- ``get_page_async()``
- ``count_async()``
- ``insert_many_async()``
- ``update_many_async()``
- ``delete_many_async()``
- ``execute_transaction_async()``
- ``with_transaction_async()``

Example Usage
-------------

.. code-block:: python

   from pydantic import BaseModel
   from wsqlite import WSQLite

   class User(BaseModel):
       id: int
       name: str
       email: str

   db = WSQLite(User, "database.db")

   # Insert
   db.insert(User(id=1, name="Alice", email="alice@example.com"))

   # Query
   users = db.get_all()
   alice_users = db.get_by_field(name="Alice")

   # Update
   db.update(1, User(id=1, name="Alice Smith", email="alice@example.com"))

   # Delete
   db.delete(1)