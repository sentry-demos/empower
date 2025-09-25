#!/bin/bash

set -e

# non-project directories
exclude_dirs=(.github _bin _mini-relay)

# Read all entries in auto-deploy.exclude file and add them to the exclude_dirs array
while IFS= read -r line; do
  # skip lines that have only whitespace or start with a #
  if [[ "$line" =~ ^[[:space:]]*$ || "$line" =~ ^# ]]; then
    continue
  fi
  line=$(echo $line | sed 's/#.*$//') # remove comments on the same line
  exclude_dirs+=("$line")
done < <(sed -e '$a\' auto-deploy.exclude) # handles missing newline at end of file

# Get all directories in the current path
all_projects=()
for item in */; do
  item=${item%/} # Remove trailing slash
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
    all_projects+=("$item")
  fi
done

echo "${all_projects[@]}" 