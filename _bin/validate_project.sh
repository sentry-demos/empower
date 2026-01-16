#!/bin/bash

path="$1"
proj=$(basename $path)

set -e 
  
if [ ! -d $path ]; then
    echo "[ERROR] Project '$proj' does not exist"
    exit 1
fi
