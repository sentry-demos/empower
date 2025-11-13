#!/bin/bash

# This is not a standalone script. It is called from ../deploy.sh that
# sets up the right environment variables and files for it.

set -e

function cleanup {
  stop.sh go $LOCAL_PORT
}
trap cleanup EXIT

if [ -z "$LOCAL_PORT" ]; then
  export LOCAL_PORT=8080
fi

echo "Starting Go server on port $LOCAL_PORT"
go run ./cmd/server/main.go

