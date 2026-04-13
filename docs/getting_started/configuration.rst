Configuration
=============

This guide explains how to configure wsqlite for different use cases.

Database Path Configuration
---------------------------

The database path can be specified as a relative or absolute path:

.. code-block:: python

   # Relative path (creates in current directory)
   db = WSQLite(User, "data.db")

   # Absolute path
   db = WSQLite(User, "/var/data/application.db")

   # In-memory database (temporary)
   db = WSQLite(User, ":memory:")

Model Configuration
-------------------

Pydantic Field Descriptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use field descriptions to add database constraints:

.. code-block:: python

   from pydantic import BaseModel, Field

   class User(BaseModel):
       id: int = Field(..., description="Primary Key")
       name: str = Field(..., description="NOT NULL")
       email: str = Field(None, description="UNIQUE")
       age: int = Field(default=0)

Supported constraints:
- ``Primary Key`` - Sets the field as primary key
- ``NOT NULL`` - Field cannot be NULL
- ``UNIQUE`` - Field values must be unique

Optional Fields
~~~~~~~~~~~~~~~~

.. code-block:: python

   from typing import Optional

   class User(BaseModel):
       id: int
       name: str
       email: Optional[str] = None  # Nullable field

Connection Settings
-------------------

SQLite connection is automatically managed. For advanced use cases:

.. code-block:: python

   from wsqlite.core.connection import get_connection, close_global_connection

   # Manual connection handling
   with get_connection("database.db") as conn:
       cursor = conn.execute("SELECT * FROM user")
       results = cursor.fetchall()

   # Clean up global connection
   close_global_connection()

Logging Configuration
-------------------

wsqlite uses loguru for logging. Configure as needed:

.. code-block:: python

   from loguru import logger

   # Add file handler
   logger.add("wsqlite.log", rotation="500 MB", retention="10 days")

   # Set specific level
   logger.level = "INFO"

Next Steps
----------

Continue to :doc:`basic_usage` for more advanced operations.