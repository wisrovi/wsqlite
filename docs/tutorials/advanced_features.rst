Advanced Features Tutorial
===========================

This tutorial covers advanced features of wsqlite.

Query Builder
-------------

.. code-block:: python

   from wsqlite import QueryBuilder

   # Build complex queries
   qb = (
       QueryBuilder("users")
       .where("age", ">", 18)
       .where("city", "IN", ["NYC", "LA", "SF"])
       .where("status", "=", "active")
       .order_by("name", descending=True)
       .limit(20)
       .offset(0)
   )

   query, values = qb.build_select()
   print(f"Query: {query}")
   print(f"Values: {values}")

   # Build count query
   count_query, count_values = qb.build_count()
   print(f"Count query: {count_query}")

Table Indexes
------------

.. code-block:: python

   from wsqlite import TableSync

   sync = TableSync(User, "advanced.db")

   # Create index
   sync.create_index(["email"], unique=True)
   sync.create_index(["last_name", "first_name"])

   # Get indexes
   indexes = sync.get_indexes()
   print(f"Indexes: {indexes}")

   # Drop index
   sync.drop_index("idx_email")

Schema Validation
-----------------

.. code-block:: python

   from wsqlite.core.repository import validate_identifier

   # Validate table/column names
   try:
       validate_identifier("users")  # OK
       validate_identifier("my_table")  # OK
       validate_identifier("users; DROP TABLE")  # Raises SQLInjectionError
   except Exception as e:
       print(f"Validation error: {e}")

Raw SQL Execution
-----------------

.. code-block:: python

   from wsqlite.core.connection import get_transaction

   with get_transaction("database.db") as txn:
       # Custom query
       result = txn.execute("SELECT COUNT(*) as cnt FROM user", ())
       print(f"Count: {result[0][0]}")

       # Aggregation
       avg_result = txn.execute("SELECT AVG(age) FROM user", ())
       print(f"Average age: {avg_result[0][0]}")