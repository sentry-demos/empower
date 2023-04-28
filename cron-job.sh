#!/bin/bash

# project: backend-cron-job
DSN=https://16b1b593fa1c4c67b925cadb496a531b@o87286.ingest.sentry.io/4505093974654976

FAILURE_PERCENT_CHANCE=10
STUCK_PERCENT_CHANCE=10

random=$(($RANDOM % 100))
if [ $random -lt $FAILURE_PERCENT_CHANCE ]; then
    echo "Attempting to call an API that is down."
    curl https://my-api-endpoint.demo-service.com/v1/list
elif [ $random -lt $(($FAILURE_PERCENT_CHANCE + $STUCK_PERCENT_CHANCE)) ]; then
    echo "Stuck (sleeping from 6 to 20 minutes)."
    sleep $(($RANDOM % 840 + 360))
    exit 0
else
    echo "Success."
    exit 0
fi