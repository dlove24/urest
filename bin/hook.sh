#!/bin/sh

# Reformat the code into the correct style
black .

# Check the code for obvious errors/style
# violations
ruff check urest

# Check for less obvious errors using 'mypy. We don't do strict (yet)
# as the MicroPython parser has problems with some of the needed type
# notation
mypy urest

# Check the documentation for sanity and conformance
# to the house style
docformatter --in-place --config ./pyproject.toml -r .
