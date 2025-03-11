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
  stop.sh google_compute_engine $FLASK_LOCAL_REDISPORT 
}
trap cleanup EXIT

# needed for caches since GCP redis doesn't have public IP
ACTIVE_ACCOUNT=$(gcloud auth list --format="value(account)" --filter="status:ACTIVE")
if [ -z "$ACTIVE_ACCOUNT" ]; then
    gcloud auth login
fi

if [ -z "$FLASK_LOCAL_REDISPORT" ]; then
    export FLASK_LOCAL_REDISPORT=6379
fi

gcloud compute ssh redis-relay --zone=us-central1-a -- -N -L $FLASK_LOCAL_REDISPORT:$FLASK_REDISHOST:6379 &

REDISPORT=$FLASK_LOCAL_REDISPORT REDISHOST=localhost flask run --port $LOCAL_PORT
