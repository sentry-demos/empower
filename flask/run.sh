#!/bin/bash

set -e

# This is not a standalone script. It is called from ../deploy.sh that
# sets up the right environemnt variables and files for it.

if [ ! -d ./venv ]; then
    python3 -m venv ./venv
fi
source venv/bin/activate
pip3 install -r requirements.txt

function cleanup {
  stop.sh python3 $LOCAL_PORT
  stop.sh gcloud 6379
}
trap cleanup EXIT

# needed for caches since GCP redis doesn't have public IP
ACTIVE_ACCOUNT=$(gcloud auth list --format="value(account)" --filter="status:ACTIVE")
if [ -z "$ACTIVE_ACCOUNT" ]; then
    gcloud auth login
fi
gcloud compute ssh redis-relay --zone=us-central1-a -- -N -L 6379:10.251.35.179:6379 &

flask run --port $LOCAL_PORT
