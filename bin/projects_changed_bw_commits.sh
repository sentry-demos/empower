#!/bin/bash

set -e

#
# Returns a space-separated list of projects that have their code changed between two commits,
#

# TODO: In the future, if/when empower-config is merged into empower, also include projects which
# have their production env-config changed.

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
toplevel_changed_array=()
while IFS= read -r line; do
  toplevel_changed_array+=("$line")
done <<< "$toplevel_changed"

# Get all deployable projects using the shared script
all_deployable_projects=($(./bin/list_deployable_projects.sh))

# Filter changed items to only include deployable projects
changed_projects=()
for item in "${toplevel_changed_array[@]}"; do
  if [[ -d "$item" ]]; then
    for deployable in "${all_deployable_projects[@]}"; do
      if [[ "$item" == "$deployable" ]]; then
        changed_projects+=("$item")
        break
      fi
    done
  fi
done

echo "${changed_projects[@]}"
