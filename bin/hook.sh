#!/bin/sh

# Reformat the code into the correct style
black --preview .

# Check for obvious errors/style violations
flake8
