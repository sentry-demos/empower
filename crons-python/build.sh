#!/bin/bash

set -e 
python3.10 -m venv env
source env/bin/activate 
pip install -r requirements.txt
