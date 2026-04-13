Exceptions Module
=================

wsqlite provides a comprehensive exception hierarchy for error handling.

Base Exception
--------------

.. autoexception:: wsqlite.exceptions.WSQLiteError
   :members:

Connection Errors
------------------

.. autoexception:: wsqlite.exceptions.ConnectionError
   :members:
   :show-inheritance:

Sync Errors
-----------

.. autoexception:: wsqlite.exceptions.TableSyncError
   :members:
   :show-inheritance:

Validation Errors
-----------------

.. autoexception:: wsqlite.exceptions.ValidationError
   :members:
   :show-inheritance:

Operation Errors
----------------

.. autoexception:: wsqlite.exceptions.OperationError
   :members:
   :show-inheritance:

SQL Injection Error
-------------------

.. autoexception:: wsqlite.exceptions.SQLInjectionError
   :members:
   :show-inheritance:

Transaction Errors
------------------

.. autoexception:: wsqlite.exceptions.TransactionError
   :members:
   :show-inheritance:

Exception Hierarchy
-------------------

.. code-block:: text

   WSQLiteError (base)
   ├── ConnectionError
   ├── TableSyncError
   ├── ValidationError
   ├── OperationError
   ├── SQLInjectionError
   └── TransactionError

Example Usage
-------------

.. code-block:: python

   from wsqlite import WSQLite
   from wsqlite.exceptions import SQLInjectionError, TransactionError

   try:
       db = WSQLite(User, "database.db")
       db.insert(user)
   except TransactionError as e:
       print(f"Transaction failed: {e}")

   # Catch specific exceptions
   try:
       # Validate identifier
       from wsqlite.core.repository import validate_identifier
       validate_identifier("users; DROP TABLE")
   except SQLInjectionError:
       print("SQL injection attempt detected!")

   # Catch all wsqlite errors
   except WSQLiteError as e:
       print(f"wsqlite error: {e}")