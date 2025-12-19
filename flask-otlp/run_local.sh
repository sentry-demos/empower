#!/bin/bash

set -e

# This is not a standalone script. It is called from ../deploy that
# sets up the right environemnt variables and files for it.

if [ ! -d ./venv ]; then
    python3 -m venv ./venv
fi
source venv/bin/activate
pip3 install -r requirements.txt


function cleanup {
  set +e
  # Kill SSH tunnel by port
  stop.sh google_compute_engine $FLASKOTLP_LOCAL_REDISPORT
  stop.sh flask $FLASKOTLP_LOCAL_PORT 
}

# Register cleanup for all possible termination signals
trap cleanup EXIT

# Set up SSH tunnel to the cloud Redis instance
# (`deploy` ensures we are authenticated with Google Cloud)
echo "Setting up SSH tunnel to Redis server at $REDIS_SERVER_IP:6379"
gcloud compute ssh redis-relay --tunnel-through-iap --zone=us-central1-a -- -N -L $FLASKOTLP_LOCAL_REDISPORT:$REDIS_SERVER_IP:6379 &


# Give the SSH tunnel time to establish
sleep 3

# Run Flask in the background and capture its PID
echo "Starting Flask server on port $FLASKOTLP_LOCAL_PORT"
gunicorn -b :$FLASKOTLP_LOCAL_PORT -w 2 --timeout 60 src.main:app
