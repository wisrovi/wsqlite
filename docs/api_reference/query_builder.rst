QueryBuilder Module
===================

The QueryBuilder provides a fluent interface for constructing SQL queries safely.

.. autoclass:: wsqlite.builders.query_builder.QueryBuilder
   :members:
   :undoc-members:
   :show-inheritance:

Methods
-------

.. csv-table::
   :header: "Method", "Description"

   "where()", "Add WHERE condition"
   "order_by()", "Add ORDER BY clause"
   "limit()", "Add LIMIT clause"
   "offset()", "Add OFFSET clause"
   "build_select()", "Build SELECT query"
   "build_count()", "Build COUNT query"
   "build_delete()", "Build DELETE query"
   "reset()", "Reset builder state"

Operators
---------

The following operators are supported in the ``where()`` method:

- ``=`` - Equals
- ``<`` - Less than
- ``>`` - Greater than
- ``<=`` - Less than or equal
- ``>=`` - Greater than or equal
- ``!=`` - Not equals
- ``LIKE`` - Pattern matching
- ``IN`` - Value in list
- ``IS NULL`` - Null check
- ``IS NOT NULL`` - Non-null check

Example Usage
-------------

.. code-block:: python

   from wsqlite import QueryBuilder

   # Build SELECT query
   qb = (
       QueryBuilder("users")
       .where("age", ">", 18)
       .where("city", "=", "NYC")
       .order_by("name", descending=True)
       .limit(10)
       .offset(20)
   )

   query, values = qb.build_select()
   print(f"Query: {query}")
   print(f"Values: {values}")

   # Output:
   # Query: SELECT * FROM users WHERE age > ? AND city = ? ORDER BY name DESC LIMIT ? OFFSET ?
   # Values: (18, 'NYC', 10, 20)

   # Build DELETE query
   qb = QueryBuilder("users").where("id", "=", 1)
   query, values = qb.build_delete()
   print(f"DELETE Query: {query}")