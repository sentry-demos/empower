#!/bin/bash

# Usage: ./create_cron_job.sh
#     Need to have TRAVIS_AUTH_TOKEN set as environment variable

headers="Content-Type=application/json,Accept=application/json,Travis-API-Version=3,Authorization=token $TRAVIS_AUTH_TOKEN"
body='{"request":{"branch":"master"}}'
url='https://api.travis-ci.org/repo/sentry-demos%2Ftest-data-automation/requests'
schedule="*/20 1,2,3,4,5,6 * * *" # Every 20 minutes from 1am - 6am
timezone="America/Los_Angeles"
JOB_NAME="TEST-DATA-AUTOMATION"

# # Code to trigger build (via travis v3 /request api)
# curl --verbose -s -X POST \
#    -H "Content-Type: application/json" \
#    -H "Accept: application/json" \
#    -H "Travis-API-Version: 3" \
#    -H "Authorization: token $TRAVIS_AUTH_TOKEN" \
#    -d "$body" \
#    $url

# Schedule as cron job on GCP
gcloud scheduler jobs create http $JOB_NAME --schedule="$schedule" --time-zone="$timezone" --uri="$url" \
   --headers="$headers" --http-method="post" --message-body="$body"
