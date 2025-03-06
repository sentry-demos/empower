#!/bin/bash

# Read input from stdin and substitute environment variables
while IFS= read -r line; do
  # Use 'eval' with 'echo' to replace environment variables
  eval "echo \"$line\""
done
