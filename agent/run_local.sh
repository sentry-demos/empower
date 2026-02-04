#!/bin/bash

set -e

function cleanup {
  stop.sh agent $AGENT_LOCAL_PORT
}
trap cleanup EXIT

# Ensure Docker (via Colima) is available - sources DOCKER_HOST
source ensure_docker.sh

# Only PORT needs explicit export (not in .env, comes from AGENT_LOCAL_PORT)
# Other vars are read from .env file by docker-compose (via env_file directive)
export PORT=$AGENT_LOCAL_PORT

docker-compose up