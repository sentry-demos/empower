#!/bin/bash

# This is not a standalone script. It is called from ../deploy.sh that
# sets up the right environment variables and files for it.

if [ "$PORT" == "" ]; then
  angular_port=4200
else
  angular_port="$PORT"
fi

function cleanup {
  stop.sh node $angular_port
}
trap cleanup EXIT

if command -v serve &> /dev/null; then
    serve -s dist/empower-angular
else
    npx serve -s dist/empower-angular
fi
