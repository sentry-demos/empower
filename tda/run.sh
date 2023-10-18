#!/bin/bash

# Run each scripts in jobs/ directory as background jobs in parallel in infinite loop 

set -e

deploy_id=$1

# Validation
if [ $(ls jobs/*.sh | wc -l) == 0 ]; then
  echo "[ERROR] No jobs found in jobs/ directory. Exiting."
  exit 1
fi

# Set up environment:

if [ ! -z $deploy_id ]; then
  env_dir="env${deploy_id}"

  if [ -d "$env_dir" ]; then
    # If the directory exists, run the activate script within it
    source "${env_dir}/bin/activate"
  else
    echo "Directory '$env_dir' does not exist."
  fi
else
  # No argument provided, find the most recently created directory matching "env*"
  env_dir="$(ls -td env* 2>/dev/null | head -n 1)"

  if [ -n "$env_dir" ]; then
    # If a directory is found, run the activate script within it
    source "${env_dir}/bin/activate"
  else
    echo "[ERROR] No 'env*' directories found. Exiting."
    exit 1
  fi
fi

source .sauce_credentials

# fetch and set release version upfront to reduce unnecessary API calls and avoid Github API rate limiting
export LATEST_REACT_NATIVE_GITHUB_RELEASE=$(python3 latest_github_release.py react_native)
export LATEST_ANDROID_GITHUB_RELEASE=$(python3 latest_github_release.py android)

# First run ALL canaries to ensure not a single one fails
for job in jobs/*.sh; do
  # set -e ensures that if any canary fails, the script will exit
  ./canary.sh $job
done

echo "[OK] All canaries passed."  

for job in jobs/*.sh; do
  echo "Starting $job to run continuously in background..."
  nohup ./loop.sh ./$job >/dev/null 2>&1 &
done

find . -maxdepth 1 -type d -name "env*" ! -name "$env_dir" -exec rm -rf {} \; -exec echo "Deleted old virtualenv directory: {}" \;
