#!/bin/bash

BATCH_SIZE=random_20 pytest -s -n 7 --ignore-glob='*_vue.py' desktop_web
