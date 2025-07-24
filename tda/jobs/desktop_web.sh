#!/bin/bash

# timeout is per-test, test_checkout is batch so can potentially take quite long
BATCH_SIZE=random_5_15 pytest --timeout=900 -s -n 7 --ignore-glob='*_vue.py' desktop_web

