#!/bin/bash

source .sauce_credentials
source env/bin/activate

# can take arguments, e.g.:
# ./deploy --env=local _tda -- ./run_local.sh desktop_web/test_homepage.py
pytest -s -n 4 $@