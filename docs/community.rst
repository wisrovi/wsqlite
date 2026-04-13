Community & Contributing
=======================

.. meta::
   :description: Join the wsqlite community and learn how to contribute
   :keywords: wsqlite, contribute, community, open source, GitHub

Overview
--------

wsqlite is an open-source project and we welcome contributions from developers 
of all skill levels. Whether you find a bug, suggest a feature, or improve 
documentation, your contributions help make wsqlite better for everyone.

Ways to Contribute
------------------

Bug Reports
~~~~~~~~~~

Found a bug? Help us fix it! When reporting bugs, please include:

* Python and wsqlite version
* Minimal reproducible code example
* Expected vs actual behavior
* Full error traceback if applicable

Submit issues at: https://github.com/wisrovi/wsqlite/issues

Feature Requests
~~~~~~~~~~~~~~~~

Have an idea for a new feature? We encourage you to:

* Search existing issues to avoid duplicates
* Describe the use case and motivation
* Outline proposed implementation approach
* Provide code examples if applicable

Pull Requests
~~~~~~~~~~~~~

We love code contributions! To submit a PR:

1. Fork the repository
2. Create a feature branch (``git checkout -b feature/amazing-feature``)
3. Make your changes with tests
4. Ensure all tests pass (``pytest``)
5. Commit with clear messages
6. Push and open a Pull Request

Development Setup
----------------

Clone the repository:

.. code-block:: bash

   git clone https://github.com/wisrovi/wsqlite.git
   cd wsqlite

Install development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

Run tests:

.. code-block:: bash

   pytest test/ -v --cov=wsqlite --cov-report=html

Build documentation:

.. code-block:: bash

   cd docs && make html

Code Standards
--------------

* Follow PEP 8 style guidelines
* Add type hints to all public APIs
* Include docstrings for classes and methods
* Write tests for new functionality (aim for 90%+ coverage)
* Update documentation for user-facing changes

Testing Guidelines
-----------------

.. code-block:: bash

   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=wsqlite --cov-report=term-missing

   # Run specific test file
   pytest test/unit/test_repository.py -v

Project Structure
-----------------

::

   wsqlite/
   ├── src/wsqlite/          # Main package source
   │   ├── core/             # Core ORM components
   │   ├── builders/         # Query builders
   │   ├── exceptions/       # Custom exceptions
   │   └── types/            # Type definitions
   ├── test/                 # Test suite
   │   ├── unit/             # Unit tests
   │   └── integration/      # Integration tests
   ├── docs/                 # Documentation
   └── examples/             # Usage examples

License
-------

By contributing to wsqlite, you agree that your contributions will be 
licensed under the MIT License.

Contact
-------

* GitHub Issues: https://github.com/wisrovi/wsqlite/issues
* Author: William Steve Rodriguez Villamizar
* LinkedIn: https://es.linkedin.com/in/wisrovi-rodriguez

Acknowledgments
---------------

Thank you to all contributors who have helped improve wsqlite!

.. todo:: Add contributor list generation script
