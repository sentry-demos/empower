#!/bin/bash

if [[ "$TDA_CONFIG" == "config.staging.yaml" ]]; then
    NUMPROCESSES = 1
else
    NUMPROCESSES = 6
fi

BATCH_SIZE=random_20 pytest -s -n $NUMPROCESSES --ignore-glob='*_vue.py' desktop_web
