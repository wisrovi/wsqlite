.. wsqlite documentation master file

.. role:: raw-html(raw)
   :format: html

.. |project| replace:: **wsqlite**

.. meta::
   :description: wsqlite - Production-ready SQLite ORM using Pydantic models
   :keywords: sqlite, orm, pydantic, python, database, async
   :author: William Steve Rodriguez Villamizar
   :author_link: https://es.linkedin.com/in/wisrovi-rodriguez

================================================================================
|project| |version| Documentation
================================================================================

.. image:: https://img.shields.io/pypi/v/wsqlite.svg
   :target: https://pypi.org/project/wsqlite/
   :alt: PyPI version
   :class: only-light

.. image:: https://img.shields.io/pypi/pyversions/wsqlite.svg
   :target: https://pypi.org/project/wsqlite/
   :alt: Python versions

.. image:: https://github.com/wisrovi/wsqlite/actions/workflows/test.yml/badge.svg
   :target: https://github.com/wisrovi/wsqlite/actions
   :alt: Tests status

.. image:: https://img.shields.io/github/license/wisrovi/wsqlite.svg
   :target: https://github.com/wisrovi/wsqlite/blob/main/LICENSE
   :alt: License

.. image:: https://img.shields.io/pypi/dm/wsqlite
   :alt: Downloads

----

Overview
--------

**wsqlite** is a production-grade SQLite ORM library engineered for modern Python 
applications. Built atop Pydantic's type validation system, it delivers type-safe 
database operations with minimal configuration overhead.

The library abstracts the complexity of SQLite schema management while providing 
enterprise-grade features including full async/await support, transaction management, 
and automatic schema synchronization.

Key Capabilities
~~~~~~~~~~~~~~~~

* **Type-Safe Schema Definition** — Leverage Pydantic models for database schemas
* **Automatic Schema Evolution** — Models automatically sync with database structure
* **Complete Async Surface** — Full async/await API for high-throughput scenarios
* **Transaction Support** — ACID-compliant transaction handling with context managers
* **Query Builder** — Fluent SQL construction with SQL injection protection
* **CLI Interface** — Integrated command-line utilities for common operations

Architecture Philosophy
~~~~~~~~~~~~~~~~~~~~~~

wsqlite embraces simplicity without sacrificing power. The architecture follows 
these core principles:

1. **Convention over Configuration** — Sensible defaults minimize setup complexity
2. **Progressive Disclosure** — Basic operations are trivial; advanced features available as needed
3. **Type Safety First** — Leverage Python's type system for compile-time error detection
4. **Zero-Cost Abstraction** — Async implementations provide performance without overhead

Quick Start
-----------

.. code-block:: python
   :linenos:

   from pydantic import BaseModel
   from wsqlite import WSQLite

   class User(BaseModel):
       id: int
       name: str
       email: str

   # Table created automatically
   db = WSQLite(User, "production.db")

   # Insert record
   db.insert(User(id=1, name="Alice", email="alice@example.com"))

   # Query records
   users = db.get_all()
   
   # Async operation
   await db.insert_async(User(id=2, name="Bob", email="bob@example.com"))

.. toctree::
   :maxdepth: 3
   :caption: 📚 Documentation
   :hidden:

   getting_started/index
   API Reference <api_reference/index>
   tutorials/index
   FAQ <faq>
   Glossary <glossary>
   Bibliography <bibliography>
   Community <community>

.. toctree::
   :maxdepth: 1
   :caption: 🔗 External Resources
   :hidden:

   GitHub Repository ⭐ <https://github.com/wisrovi/wsqlite>
   PyPI Package <https://pypi.org/project/wsqlite/>
   Report Issues 🐛 <https://github.com/wisrovi/wsqlite/issues>
   William Rodriguez on LinkedIn 💼 <https://es.linkedin.com/in/wisrovi-rodriguez>

.. raw:: html

   <hr>

Indices and Tables
==================

* :ref:`genindex` — Complete API reference
* :ref:`modindex` — Module overview
* :ref:`search` — Full-text search
* :ref:`glossary` — Terminology reference

----

.. include:: ../CHANGELOG.md
   :start-line: 1
   :end-line: 50

*© 2024 William Steve Rodriguez Villamizar. MIT License.*

.. sidebar::
   :class: margin-toc
   
   **Table of Contents**
   
   .. toctree::
      :maxdepth: 2
      :titlesonly:
      
      getting_started/index
      api_reference/index
      tutorials/index