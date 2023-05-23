#!/bin/bash

set -e

#
# Returns a space-separated list of projects that have their code changed between two commits,
#

# TODO: In the future, if/when empower-config is merged into empower, also include projects which
# have their production env-config changed.

# non-project directories and projects with missing deploy scripts
exclude_dirs=(".github" "env-config" "bin" "vue" "ruby") 

# Parse and validate command-line arguments
base="$1"
head="$2"
if [[ "$base" == "" || "$head" == "" ]]; then
  echo "$0: [error] missing required command-line arguments. Usage: $0 BASE_COMMIT HEAD_COMMIT"
  exit 1
fi

# Get a list of top-level directories and files that have been changed between the two commits
toplevel_changed=$(git diff --name-only $base $head | cut -d/ -f1 | uniq)

# Convert the newline-separated list to an array
while IFS= read -r line; do
  toplevel_changed_array+=("$line")
done <<< "$toplevel_changed"

# Filter to only include non-excluded directories
changed_projects=()
for item in "${toplevel_changed_array[@]}"; do
  # Check if the item is a file
  if [[ -d "$item" ]]; then
    x=0
    for x_dir in "${exclude_dirs[@]}"; do
        if [[ "$item" == "$x_dir" ]]; then
            x=1
            break
        fi
    done
    if [[ "$x" == "1" ]]; then
        continue
    fi
    changed_projects+=("$item")
  fi
done

echo "${changed_projects[@]}"