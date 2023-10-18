#!/bin/bash

deploy_id=$1

set -e 
virtualenv --python=`which python3.8` "env$deploy_id"
source "env$deploy_id/bin/activate"
pip install -r requirements.txt
