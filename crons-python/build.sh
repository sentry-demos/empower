#!/bin/bash

set -e 
python3.12 -m venv env
source env/bin/activate 
pip install -r requirements.txt
