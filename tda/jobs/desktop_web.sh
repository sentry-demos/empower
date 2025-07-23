#!/bin/bash

# 0.0 - 0.3 cexp (flask) depening on cexp cycle
# 0.7 non-cexp
#   0.42-0.6 flask
#   0.056-0.08 each of {express,springboot,laravel,rails,aspnetcore}
# flask total = 0.6 - 0.72
BATCH_SIZE=random_5_15 pytest --timeout=1200 -s -n 7 --ignore-glob='*_vue.py' desktop_web

