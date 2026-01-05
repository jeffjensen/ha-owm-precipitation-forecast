#!/bin/bash
# Validation script
set -e
echo "Running validation..."
ruff check .
black --check .
mypy custom_components
pytest --cov
echo "✓ All checks passed!"
