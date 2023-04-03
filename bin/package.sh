#!/bin/sh

# Check with Flake8 for obvious problems
flake8

# Run the tests to check for breakage
pytest

# Build the current package
python3 -m build

# Upload to the PyPi repository
twine upload dist/*
