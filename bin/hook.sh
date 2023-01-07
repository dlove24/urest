#!/bin/sh

# Reformat the code into the correct style
black .

# Regenerate the documentation. The module is
# unlikely to be installed on the doc build machine
# so read the files directly
pdoc --html --force --output-dir docs .
