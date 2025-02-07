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
  echo "Cleaning up processes..."

  # Kill Flask process if running
  if [ -n "$FLASK_PID" ] && kill -0 $FLASK_PID 2>/dev/null; then
    echo "Stopping Flask server..."
    kill -TERM $FLASK_PID 2>/dev/null || true
  fi

  # Kill Celery workers
  echo "Stopping Celery workers..."
  pkill -f "celery worker" || true
  if [ -n "$CELERY_PID" ] && kill -0 $CELERY_PID 2>/dev/null; then
    kill -TERM $CELERY_PID 2>/dev/null || true
  fi

  # Kill Redis relay
  if [ -n "$REDIS_RELAY_PID" ] && kill -0 $REDIS_RELAY_PID 2>/dev/null; then
    echo "Stopping Redis relay..."
    kill -TERM $REDIS_RELAY_PID 2>/dev/null || true
  fi

  # Use stop.sh as fallback
  stop.sh python3 $LOCAL_PORT 2>/dev/null || true
  stop.sh gcloud 6379 2>/dev/null || true

  echo "Cleanup complete"
}

# Trap signals to ensure cleanup happens
trap cleanup EXIT INT TERM

# needed for caches since GCP redis doesn't have public IP
ACTIVE_ACCOUNT=$(gcloud auth list --format="value(account)" --filter="status:ACTIVE")
if [ -z "$ACTIVE_ACCOUNT" ]; then
    gcloud auth login
fi

echo "Starting Redis relay..."
gcloud compute ssh redis-relay --zone=us-central1-a -- -N -L 6379:10.251.35.179:6379 &
REDIS_RELAY_PID=$!

# wait for relay to be setup before celery connects
sleep 1

echo "Starting Celery worker..."
celery -A src.queues.email_subscribe worker -l INFO &
CELERY_PID=$!

echo "Starting Flask server on port $LOCAL_PORT..."
flask run --port $LOCAL_PORT &
FLASK_PID=$!

echo "All services started. Press Ctrl+C to stop."

# Wait for any signal that would cause the script to exit
wait $FLASK_PID
