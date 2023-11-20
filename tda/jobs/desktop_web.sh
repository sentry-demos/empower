#!/bin/bash

BATCH_SIZE=random_20 REPEATABLE_RANDOM=1 pytest -s -n 7 --ignore-glob='*_vue.py' desktop_web
