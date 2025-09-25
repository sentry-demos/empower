#!/bin/bash

# This is not a standalone script. It is called from ../deploy.sh that
# sets up the right environment variables and files for it.

function cleanup {
  stop.sh node $ANGULAR_LOCAL_PORT
}
trap cleanup EXIT

if command -v serve &> /dev/null; then
    serve -s dist/empower-angular -l $ANGULAR_LOCAL_PORT
else
    npx serve -s dist/empower-angular -l $ANGULAR_LOCAL_PORT
fi
