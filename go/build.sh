#!/bin/bash
set -e

if ! command -v go >/dev/null 2>&1; then
  echo "Go toolchain is required"
  exit 1
fi

go mod tidy

# Build server binary for deployment
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o server ./cmd/server

# Optionally build worker (not used on App Engine standard)
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o worker ./cmd/worker || true

