#!/bin/bash

if [ "$PORT" == "" ]; then
  # https://create-react-app.dev/docs/advanced-configuration/
  react_port=3000
else
  react_port="$PORT"
fi

function cleanup {
  stop.sh node $react_port
}
trap cleanup EXIT

if command -v serve &> /dev/null; then
    serve -s build
else
    npx serve -s build
fi
