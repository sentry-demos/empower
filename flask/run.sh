#!/bin/bash

if [ ! -d ./venv ]; then 
    python3 -m venv ./venv
fi
source venv/bin/activate
pip3 install -r requirements.txt

function cleanup {
  stop.sh python3 8080
  if [[ "$VIRTUAL_ENV" != "" ]]; then
    deactivate
  fi
}
trap cleanup EXIT

python3 main.py
