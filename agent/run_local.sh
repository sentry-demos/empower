#!/bin/bash

set -e

function cleanup {
  stop.sh agent $AGENT_LOCAL_PORT
}
trap cleanup EXIT

# Ensure Docker (via Colima) is available
ensure_docker() {
  # Check for Homebrew
  if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew is required to install dependencies. Install from https://brew.sh"
    exit 1
  fi

  # Install Docker CLI if not present
  if ! command -v docker &> /dev/null; then
    echo "Installing Docker CLI..."
    brew install docker
  fi

  # Install Colima if not present
  if ! command -v colima &> /dev/null; then
    echo "Installing Colima..."
    brew install colima
  fi

  # Start Colima if not running
  if ! colima status &> /dev/null; then
    echo "Starting Colima..."
    colima start
  fi
}

ensure_docker

export API_PORT=$AGENT_LOCAL_PORT
export AGENT_OPENAI_API_KEY=$AGENT_OPENAI_API_KEY
export AGENT_DSN=$AGENT_DSN
export AGENT_SENTRY_ENVIRONMENT=$AGENT_SENTRY_ENVIRONMENT
export MCP_URL=$MCP_URL

docker-compose up