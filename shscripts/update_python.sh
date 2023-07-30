#!/bin/bash

# Update python dependencies after a major python update

rm -r .venv .pipcache

# This script executes inside the docker container

PIPCACHE_DIR=./.pipcache
VENV_DIR=.venv
# Create virtual enviroment
python -m venv "$VENV_DIR" && \
mkdir "$PIPCACHE_DIR"

# Activate virtual enviroment
source "$VENV_DIR/bin/activate" && \

# Install pipenv first
pip install --cache-dir "$PIPCACHE_DIR" pipenv && \

# Install the rest of python dependencies with pipenv 
pipenv install --dev
