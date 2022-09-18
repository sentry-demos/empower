#!/bin/bash

function cleanup {
  stop.sh node 3000 
}
trap cleanup EXIT

if command -v serve &> /dev/null; then
    serve -s build
else
    npx serve -s build
fi
