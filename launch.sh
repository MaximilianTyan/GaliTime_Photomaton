#!/bin/bash

# Checks for updates
git reset --soft HEAD
git pull --ff

# Activating virtual environment
source env/bin/activate

# Launching galitime module (galitime/__main__.py)
python3 -m galitime

# Exiting virtual environment
deactivate