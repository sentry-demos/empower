#!/bin/bash

set -e

function cleanup {
  stop.sh agent $AGENT_LOCAL_PORT
}
trap cleanup EXIT

# Ensure Docker (via Colima) is available - sources DOCKER_HOST
source ensure_docker.sh

export PORT=$AGENT_LOCAL_PORT
export AGENT_OPENAI_API_KEY=$AGENT_OPENAI_API_KEY
export AGENT_DSN=$AGENT_DSN
export AGENT_SENTRY_ENVIRONMENT=$AGENT_SENTRY_ENVIRONMENT
export MCP_URL=$MCP_URL

docker-compose up