#!/bin/sh

# Build the current package
python3 -m build

# Upload to the PyPi repository
twine upload dist/*
