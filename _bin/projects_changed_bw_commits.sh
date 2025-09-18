#!/bin/bash

set -e

#
# Returns a space-separated list of projects that have their code changed between two commits,
# including projects affected by changes in production.env
#

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
all_deployable_projects=($(./_bin/list_deployable_projects.sh))

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

# Check for changes in production.env and identify affected projects
if git diff --name-only $base $head | grep -q "^production\.env$"; then
  # Get the changed lines in production.env
  changed_lines=$(git diff $base $head -- production.env | grep "^[+-]" | grep -v "^[+-][+-][+-]")
  
  # Extract prefixes from changed lines and match against deployable projects
  while IFS= read -r line; do
    # Remove the +/- prefix and extract the variable name
    var_name=$(echo "$line" | sed 's/^[+-]//' | cut -d'=' -f1)
    
    # Extract the first part before underscore as potential project name
    prefix=$(echo "$var_name" | cut -d'_' -f1)
    
    # Normalize prefix: convert to uppercase and remove non-alphanumeric characters
    normalized_prefix=$(echo "$prefix" | tr '[:lower:]' '[:upper:]' | tr -cd '[:alnum:]')
    
    # Check if this normalized prefix matches any deployable project
    for deployable in "${all_deployable_projects[@]}"; do
      # Normalize deployable project name: convert to uppercase and remove non-alphanumeric characters
      normalized_deployable=$(echo "$deployable" | tr '[:lower:]' '[:upper:]' | tr -cd '[:alnum:]')
      
      if [[ "$normalized_prefix" == "$normalized_deployable" ]]; then
        # Check if this project is not already in the changed_projects array
        found=false
        for existing in "${changed_projects[@]}"; do
          if [[ "$existing" == "$deployable" ]]; then
            found=true
            break
          fi
        done
        if [[ "$found" == false ]]; then
          changed_projects+=("$deployable")
        fi
        break
      fi
    done
  done <<< "$changed_lines"
fi

echo "${changed_projects[@]}"
