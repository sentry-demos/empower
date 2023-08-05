#!/bin/bash

if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS uses BSD sed
  # pass all arguments
  sed -i '' "$@"
else
  # Assume GNU sed for Linux
  sed -i "$@"
fi
