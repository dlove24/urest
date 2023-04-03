#!/bin/sh

# Reformat the code into the correct style
black .

# Check for obvious errors/style violations
flake8
