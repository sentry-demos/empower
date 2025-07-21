#!/bin/bash

set -e 
# old venv directory should already be removed by deploy_tda.sh
python3.10 -m venv env
source env/bin/activate 
pip install -r requirements.txt
