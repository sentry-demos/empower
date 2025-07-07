#!/bin/bash

# Run each scripts in jobs/ directory as background jobs in parallel in infinite loop 

set -e

# Validation
if [ $(ls jobs/*.sh | wc -l) == 0 ]; then
  echo "[ERROR] No jobs found in jobs/ directory. Exiting."
  exit 1
fi

# Set up environment:
# fetch and set release version upfront to reduce unnecessary API calls and avoid Github API rate limiting
source env/bin/activate
source .sauce_credentials
export LATEST_REACT_NATIVE_GITHUB_RELEASE=$(python3 latest_github_release.py react_native)
export LATEST_ANDROID_GITHUB_RELEASE=$(python3 latest_github_release.py android)

# First run ALL canaries to ensure not a single one fails
for job in jobs/*.sh; do
  # set -e ensures that if any canary fails, the script will exit
  ./canary.sh $job
done

echo "[OK] All canaries passed."  

for job in jobs/*.sh; do
  job_name=$(basename $job .sh)
  echo "Starting $job to run continuously in background..."
  nohup ./loop.sh ./$job >/var/log/tda-$job_name.log 2>&1 &
done
