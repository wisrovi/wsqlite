Connection Module
=================

This module provides connection management for SQLite databases.

Transaction
-----------

.. autoclass:: wsqlite.core.connection.Transaction
   :members:
   :undoc-members:
   :show-inheritance:

AsyncTransaction
-----------------

.. autoclass:: wsqlite.core.connection.AsyncTransaction
   :members:
   :undoc-members:
   :show-inheritance:

Connection Functions
--------------------

.. autofunction:: wsqlite.core.connection.get_connection

.. autofunction:: wsqlite.core.connection.get_async_connection

.. autofunction:: wsqlite.core.connection.get_transaction

.. autofunction:: wsqlite.core.connection.get_async_transaction

.. autofunction:: wsqlite.core.connection.close_global_connection

Exception Handling
------------------

Connection-related exceptions are defined in :mod:`wsqlite.exceptions`:

- :exc:`wsqlite.exceptions.ConnectionError`
- :exc:`wsqlite.exceptions.TransactionError`

Example Usage
-------------

.. code-block:: python

   from wsqlite.core.connection import get_connection, Transaction

   # Using connection context manager
   with get_connection("database.db") as conn:
       cursor = conn.execute("SELECT COUNT(*) FROM users")
       count = cursor.fetchone()[0]
       print(f"Total users: {count}")

   # Using transaction
   with Transaction("database.db") as txn:
       txn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
       txn.commit()