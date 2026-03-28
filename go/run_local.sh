#!/bin/bash

# This is not a standalone script. It is called from ../deploy that
# sets up the right environment variables and files for it.

set -e

# Reference DB secrets so the deploy script fetches them from GCP Secret Manager.
# These are passed as env vars to the Go server process.
required_secrets="$DB_HOST $DB_DATABASE $DB_USERNAME $DB_PASSWORD $DB_CLOUD_SQL_CONNECTION_NAME"

function cleanup {
  stop.sh go $LOCAL_PORT
}
trap cleanup EXIT

if [ -z "$LOCAL_PORT" ]; then
  export LOCAL_PORT=8080
fi

echo "Starting Go server on port $LOCAL_PORT"
go run ./cmd/server/main.go
