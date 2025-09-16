#!/bin/bash

set -e

# This is a local version of run.sh that uses local Redis instead of cloud Redis

if [ ! -d ./venv ]; then
    python3 -m venv ./venv
fi
source venv/bin/activate
pip3 install -r requirements.txt

# Store PIDs for cleanup
CELERY_PID=""

function cleanup {
  # Kill Celery worker by PID
  if [ -n "$CELERY_PID" ]; then
    kill -9 $CELERY_PID 2>/dev/null || true
  fi
  
  stop.sh python3 $LOCAL_PORT
}

# Register cleanup for all possible termination signals
trap cleanup EXIT

if [ -z "$LOCAL_PORT" ]; then
    export LOCAL_PORT=8080
fi

# For local development, use localhost Redis
export FLASK_REDISHOST=localhost
export REDIS_URL=redis://localhost:6379

# Start Celery worker
echo "Starting Celery worker..."
celery -A src.queues.email_subscribe worker -l INFO --concurrency=1 &
CELERY_PID=$!
echo "Celery worker started with PID: $CELERY_PID"

# Run Flask
echo "Starting Flask server on port $LOCAL_PORT"
gunicorn -b :$LOCAL_PORT -w 2 --timeout 60 src.main:app
