#!/bin/bash

BATCH_SIZE=random_20 pytest -s -n 13 --ignore-glob='*_vue.py' desktop_web
