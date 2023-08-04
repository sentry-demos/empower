#!/bin/bash

# Execute command in a loop infinitely, whether it fails or succeeds

# usage: ./loop.sh command arg1 arg2 ...

while true; do 
  "$@"
done
