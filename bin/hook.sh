#!/bin/sh

# Reformat the code into the correct style
black .

# Regenerate the documentation
pdoc --html --force --output-dir doc http
