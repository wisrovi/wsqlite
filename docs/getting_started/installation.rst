Installation
============

This guide covers the installation process for wsqlite across different environments.

Requirements
------------

- Python 3.9 or higher
- pydantic >= 2.0.0
- loguru >= 0.7.0
- click >= 8.0.0
- aiosqlite >= 0.19.0

Installation Methods
-------------------

Using pip (Recommended)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install wsqlite

Using pip with extras
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install wsqlite[dev]

This installs the package with development dependencies including 
testing frameworks and code quality tools.

From Source
~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/wisrovi/wsqlite.git
   cd wsqlite
   pip install -e ".[dev]"

Verification
------------

To verify the installation was successful:

.. code-block:: python

   import wsqlite
   print(wsqlite.__version__)

   # Should output: 1.0.0

Dependencies Overview
--------------------

+------------------+----------+------------------------------------------+
| Package          | Version  | Purpose                                  |
+==================+==========+==========================================+
| pydantic         | >=2.0.0  | Schema definition and validation         |
+------------------+----------+------------------------------------------+
| loguru           | >=0.7.0  | Logging framework                         |
+------------------+----------+------------------------------------------+
| click            | >=8.0.0  | CLI interface                            |
+------------------+----------+------------------------------------------+
| aiosqlite        | >=0.19.0 | Async SQLite operations                  |
+------------------+----------+------------------------------------------+

Next Steps
----------

Continue to :doc:`quickstart` to learn the basics of wsqlite.