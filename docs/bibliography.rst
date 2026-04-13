Bibliography and Reference Resources
=====================================

This section provides curated external resources for deep diving into the 
technologies and patterns used in wsqlite.

Primary References
------------------

Python Ecosystem
~~~~~~~~~~~~~~~~

.. rst-class:: reference-list

* **Python Documentation** — https://docs.python.org/3/
   Official Python language reference and library documentation.

* **PEP 484 — Type Hints** — https://peps.python.org/pep-0484/
   Foundation for type-safe Python development.

* **Python asyncio** — https://docs.python.org/3/library/asyncio.html
   Async/await patterns and concurrency primitives.

Pydantic Framework
~~~~~~~~~~~~~~~~~~

* **Pydantic Official** — https://docs.pydantic.dev/
   Data validation using Python type annotations.

* **Pydantic GitHub** — https://github.com/pydantic/pydantic
   Source code and issue tracking.

SQLite Documentation
~~~~~~~~~~~~~~~~~~~

* **SQLite Official** — https://www.sqlite.org/docs.html
   Complete SQLite reference documentation.

* **SQLite Python Documentation** — https://docs.python.org/3/library/sqlite3.html
   Python's built-in SQLite bindings.

AsyncIO Libraries
~~~~~~~~~~~~~~~~~

* **aiosqlite** — https://aiosqlite.readthedocs.io/
   Async SQLite wrapper for asyncio applications.

* **Loguru** — https://loguru.readthedocs.io/
   Python logging library with simplified API.

Advanced Patterns
----------------

Database Design
~~~~~~~~~~~~~~~

* **Database Normalization** — https://en.wikipedia.org/wiki/Database_normalization
   Theory of relational database design.

* **ACID Properties** — https://en.wikipedia.org/wiki/ACID
   Atomicity, Consistency, Isolation, Durability guarantees.

ORM Patterns
~~~~~~~~~~~~

* **SQLAlchemy Documentation** — https://docs.sqlalchemy.org/
   Mature ORM patterns and techniques.

* **Active Record Pattern** — https://en.wikipedia.org/wiki/Active_record_pattern
   Domain-driven design pattern for data persistence.

Testing & Quality
-----------------

Testing Frameworks
~~~~~~~~~~~~~~~~~~

* **pytest** — https://pytest.org/
   Comprehensive Python testing framework.

* **pytest-asyncio** — https://pytest-asyncio.readthedocs.io/
   Async test support for pytest.

* **Coverage.py** — https://coverage.readthedocs.io/
   Code coverage measurement tool.

Code Quality
~~~~~~~~~~~~

* **Ruff** — https://docs.astral.sh/ruff/
   Fast Python linter written in Rust.

* **Black** — https://black.readthedocs.io/
   Uncompromising code formatter.

* **MyPy** — https://mypy.readthedocs.io/
   Static type checker for Python.

Security
--------

SQL Injection Prevention
~~~~~~~~~~~~~~~~~~~~~~~~

* **OWASP SQL Injection** — https://owasp.org/www-community/attacks/SQL_Injection
   Comprehensive guide to SQL injection attacks and prevention.

* **Python SQL Injection Prevention** — https://stackoverflow.com/questions/4217509/python-sql-injection-prevention
   Parameterized queries in Python.

Author Resources
---------------

* **William Rodriguez** — https://es.linkedin.com/in/wisrovi-rodriguez
   LinkedIn profile - Technology Evangelist

* **wsqlite GitHub** — https://github.com/wisrovi/wsqlite
   Source code, issues, and contributions

Related Projects
----------------

Similar libraries in the w-database series:

* **wpostgresql** — https://github.com/wisrovi/wpostgresql
   PostgreSQL ORM with similar API

* **wmysql** — https://github.com/wisrovi/wmysql
   MySQL ORM implementation

* **wmariadb** — https://github.com/wisrovi/wmariadb
   MariaDB ORM implementation

* **wdatabricks** — https://github.com/wisrovi/wdatabricks
   Databricks SQL connector

* **wSnowflake** — https://github.com/wisrovi/wSnowflake
   Snowflake database ORM

* **wElasticsearch** — https://github.com/wisrovi/wElasticsearch
   Elasticsearch Python client

Learning Paths
-------------

Beginner Path
~~~~~~~~~~~~~

1. Read :doc:`../getting_started/installation`
2. Complete :doc:`../getting_started/quickstart`
3. Review :doc:`../tutorials/crud_operations`
4. Experiment with examples in ``examples/`` directory

Intermediate Path
~~~~~~~~~~~~~~~~~

1. Explore :doc:`../tutorials/async_operations`
2. Learn :doc:`../tutorials/transactions`
3. Understand :doc:`../api_reference/query_builder`
4. Read :doc:`../faq`

Advanced Path
~~~~~~~~~~~~~

1. Study source code in ``src/wsqlite/``
2. Contribute to development
3. Review architecture in :doc:`../api_reference/index`
4. Optimize performance with :doc:`../tutorials/advanced_features`

.. rst-class:: note

   **Contributions Welcome**
   
   This documentation is open source. Submit improvements via Pull Request
   on GitHub: https://github.com/wisrovi/wsqlite