# Documentation

Sphinx-based documentation for wsqlite library.

## Structure

```
docs/
├── tutorials/           # Tutorial guides
│   ├── crud_operations.rst
│   ├── async_operations.rst
│   ├── transactions.rst
│   ├── bulk_operations.rst
│   ├── pagination.rst
│   ├── connection.rst
│   └── advanced_features.rst
├── api_reference/      # API documentation
│   ├── repository.rst
│   ├── query_builder.rst
│   ├── table_sync.rst
│   ├── exceptions.rst
│   └── index.rst
├── getting_started/    # Getting started guides
├── conf.py            # Sphinx configuration
├── index.rst          # Documentation index
├── Makefile          # Build documentation
└── _static/          # Static assets
```

## Building Documentation

```bash
cd docs
make html
```

## Viewing Documentation

```bash
# Serve locally
python -m http.server 8000
# Then open http://localhost:8000
```