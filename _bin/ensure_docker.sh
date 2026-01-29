#!/bin/bash

# Ensure Docker (via Colima) is available for local development
# Usage: source this script or call it directly
#   source ensure_docker.sh  # exports DOCKER_HOST to current shell
#   ./ensure_docker.sh       # just verifies docker is working

set -e

# Set Docker host to Colima's socket (must be set before any docker commands)
export DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock"

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

  # Install docker-compose if not present
  if ! command -v docker-compose &> /dev/null; then
    echo "Installing docker-compose..."
    brew install docker-compose
  fi

  # Install Colima if not present
  if ! command -v colima &> /dev/null; then
    echo "Installing Colima..."
    brew install colima
  fi

  # Start Colima if not running or socket doesn't exist
  if ! colima status &> /dev/null || [ ! -S "${HOME}/.colima/default/docker.sock" ]; then
    echo "Starting Colima..."
    colima start
  fi

  # Verify Docker is working
  echo "Verifying Docker connection (DOCKER_HOST=$DOCKER_HOST)..."
  if ! docker info &> /dev/null; then
    echo "Error: Docker not responding. Trying to restart Colima..."
    colima stop 2>/dev/null || true
    colima start
    if ! docker info &> /dev/null; then
      echo "Error: Docker still not responding after restarting Colima"
      exit 1
    fi
  fi
  echo "Docker is ready."
}

ensure_docker
