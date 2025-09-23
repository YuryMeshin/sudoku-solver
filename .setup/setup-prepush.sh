#!/bin/bash
set -e

# Detect local Python version
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Detected local Python version: $PY_VERSION"

# Create .pre-commit-config.yaml
cat > .pre-push-config.yaml <<EOL
repos:
  - repo: local
    hooks:
      - id: pytest-functional
        name: Run functional tests
        entry: python$PY_VERSION -m pytest tests/functional
        language: system
        pass_filenames: false

      - id: pytest-unit
        name: Run unit tests
        entry: python$PY_VERSION -m pytest tests/unit
        language: system
        pass_filenames: false
EOL

echo ".pre-push-config.yaml created."

# Install pre-push hook
pre-commit install --hook-type pre-push
echo "Pre-push hook installed. Functional tests run first, then unit tests."
