#!/bin/bash

set -e

# This is not a standalone script. It is called from ../deploy.sh that
# sets up the right environemnt variables and files for it.

if [ ! -d ./venv ]; then
    python3 -m venv ./venv
fi
source venv/bin/activate
pip3 install -r requirements.txt

# Store PIDs for cleanup
REDIS_RELAY_PID=""
CELERY_PID=""
FLASK_PID=""

function cleanup {
  # First, kill the specific processes we started
  if [ -n "$CELERY_PID" ]; then
    kill -9 $CELERY_PID 2>/dev/null || true
  fi

  if [ -n "$REDIS_RELAY_PID" ]; then
    kill -9 $REDIS_RELAY_PID 2>/dev/null || true
  fi

  if [ -n "$FLASK_PID" ]; then
    kill -9 $FLASK_PID 2>/dev/null || true
  fi
}

# Register cleanup for all possible termination signals
trap cleanup EXIT INT TERM HUP QUIT

# needed for caches since GCP redis doesn't have public IP
ACTIVE_ACCOUNT=$(gcloud auth list --format="value(account)" --filter="status:ACTIVE")
if [ -z "$ACTIVE_ACCOUNT" ]; then
    gcloud auth login
fi

if [ -z "$FLASK_LOCAL_REDISPORT" ]; then
    export FLASK_LOCAL_REDISPORT=6379
fi

if [ -z "$LOCAL_PORT" ]; then
    export LOCAL_PORT=8080
fi

# Set up SSH tunnel to the cloud Redis instance
echo "Setting up SSH tunnel to Redis server at $FLASK_REDIS_SERVER_IP:6379"
gcloud compute ssh redis-relay --zone=us-central1-a -- -N -L $FLASK_LOCAL_REDISPORT:$FLASK_REDIS_SERVER_IP:6379 &
REDIS_RELAY_PID=$!
echo "SSH tunnel started with PID: $REDIS_RELAY_PID"

# Give the SSH tunnel time to establish
sleep 3

# Start Celery worker
echo "Starting Celery worker..."
celery -A src.queues.email_subscribe worker -l INFO --concurrency=1 &
CELERY_PID=$!
echo "Celery worker started with PID: $CELERY_PID"

# Run Flask in the background and capture its PID
echo "Starting Flask server on port $LOCAL_PORT"
flask run --port $LOCAL_PORT &
FLASK_PID=$!
echo "Flask server started with PID: $FLASK_PID"

# Wait for Flask to exit
wait $FLASK_PID
