TableSync Module
================

This module handles table synchronization between Pydantic models and SQLite.

.. autoclass:: wsqlite.core.sync.TableSync
   :members:
   :undoc-members:
   :show-inheritance:

AsyncTableSync
--------------

.. autoclass:: wsqlite.core.sync.AsyncTableSync
   :members:
   :undoc-members:
   :show-inheritance:

Methods Overview
-----------------

.. csv-table::
   :header: "Method", "Description"

   "create_if_not_exists()", "Create table if it doesn't exist"
   "sync_with_model()", "Sync table with model (add new columns)"
   "table_exists()", "Check if table exists"
   "drop_table()", "Drop the table"
   "get_columns()", "Get list of column names"
   "create_index()", "Create an index"
   "drop_index()", "Drop an index"
   "get_indexes()", "Get list of indexes"

Example Usage
-------------

.. code-block:: python

   from pydantic import BaseModel
   from wsqlite import TableSync

   class User(BaseModel):
       id: int
       name: str
       email: str

   sync = TableSync(User, "database.db")

   # Create table
   sync.create_if_not_exists()

   # Check if exists
   if sync.table_exists():
       print("Table exists!")

   # Get columns
   columns = sync.get_columns()
   print(f"Columns: {columns}")

   # Create index
   sync.create_index(["email"], unique=True)

   # Get indexes
   indexes = sync.get_indexes()
   print(f"Indexes: {indexes}")