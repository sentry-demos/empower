#!/bin/bash

set -e 
#virtualenv --python=`which python3.8` env
# old venv directory should already be removed by deploy_tda.sh
python3 -m venv env
source env/bin/activate 
pip install -r requirements.txt
