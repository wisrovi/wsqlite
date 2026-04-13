FAQ
===

Frequently Asked Questions about wsqlite.

General Questions
-----------------

**What is wsqlite?**
   wsqlite is a production-ready SQLite ORM library that uses Pydantic models for type-safe database operations.

**What Python versions are supported?**
   wsqlite supports Python 3.9 and higher.

**Is wsqlite production-ready?**
   Yes, wsqlite is released as version 1.0.0 LTS with comprehensive test coverage.

Installation
------------

**How do I install wsqlite?**
   .. code-block:: bash

      pip install wsqlite

**What are the dependencies?**
   - pydantic >= 2.0.0
   - loguru >= 0.7.0
   - click >= 8.0.0
   - aiosqlite >= 0.19.0

Usage Questions
--------------

**How do I create a table?**
   Simply instantiate WSQLite with your Pydantic model:
   .. code-block:: python

      from wsqlite import WSQLite
      db = WSQLite(MyModel, "database.db")

**How do I handle async operations?**
   Use the async methods with _async suffix:
   .. code-block:: python

      await db.insert_async(user)
      users = await db.get_all_async()

**Can I use transactions?**
   Yes, use execute_transaction or with_transaction methods.

**How do I add indexes?**
   Use the TableSync class:
   .. code-block:: python

      sync = TableSync(Model, "db.db")
      sync.create_index(["column_name"])

Troubleshooting
--------------

**I'm getting "readonly database" errors**
   Ensure you have write permissions to the database file location.

**How do I handle schema changes?**
   The sync_with_model() method automatically adds new columns when your model changes.

**Can I use multiple databases?**
   Yes, create separate WSQLite instances for each database file.

Performance
-----------

**Is wsqlite fast?**
   Yes, it uses optimized SQLite operations and supports async for high-performance applications.

**Does it support connection pooling?**
   SQLite is embedded, so connection pooling is not needed. Use global connection for best performance.

**How does it compare to other ORMs?**
   wsqlite provides a simpler, more Pythonic interface with full Pydantic integration.

Development
-----------

**How do I run tests?**
   .. code-block:: bash

      pip install -e ".[dev]"
      pytest

**How do I contribute?**
   Fork the repository and submit a pull request on GitHub.