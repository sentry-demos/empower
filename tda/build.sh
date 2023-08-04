#!/bin/bash

set -e 
virtualenv --python=`which python3.8` env
source env/bin/activate 
pip install -r requirements.txt