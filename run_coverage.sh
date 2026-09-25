#!/usr/bin/env bash
set -e

echo "=== Calculating Code Coverage for WSQLite ==="
PYTHONPATH=src pytest --cov=wsqlite --cov-report=term-missing --cov-report=html test/unit/
echo "=== Coverage Report Generated in htmlcov/index.html ==="
