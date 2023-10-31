#!/bin/bash

set -e 
#virtualenv --python=`which python3.8` env
python3.10 -m venv env
source env/bin/activate 
pip install -r requirements.txt
