#!/bin/bash

# This is not a standalone script. It is called from ../deploy that
# sets up the right environment variables and files for it.

function cleanup {
  stop.sh node $REACT_LOCAL_PORT
}
trap cleanup EXIT

# Redirect stdin to prevent interactive mode from capturing terminal
PORT=$REACT_LOCAL_PORT npx serve -s build < /dev/null