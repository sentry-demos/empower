#!/bin/bash

set -e

sentry_project="$1"
dsn="$2"
error_message="$3"

# Verify that <PROJ>_SENTRY_PROJECT and <PROJ>_APP_DSN point to the same project
if [ "$SENTRY_AUTH_TOKEN" == "" ]; then
    echo "$0 [ERROR] SENTRY_AUTH_TOKEN must be defined. See https://docs.sentry.io/product/cli/configuration/
        In GitHub Actions environment this means that corresponding secret is not set."
    exit 2
fi
api_response=$(curl https://sentry.io/api/0/projects/ \
    -H 'Authorization: Bearer '"$SENTRY_AUTH_TOKEN" 2>/dev/null)
id_proj=$(echo "$api_response" | grep -Eo '"id":"([^"]*)","slug":"(.*?)"' | sed 's/"id":"//g' | sed 's/","slug":"/ /g' | sed 's/"//g')

project_id_from_slug=$(echo "$id_proj" | grep $sentry_project | head -1 | cut -d ' ' -f 1)
if [ "$project_id_from_slug" == "" ]; then
    echo "$0 [ERROR] Unable to get project id using Sentry API. Wrong auth token? Response:"
    echo "$resp"
    exit 2
fi

project_id_from_dsn=$(echo $dsn | cut -d / -f 4)
if [ "$project_id_from_slug" != "$project_id_from_dsn" ]; then
    echo "$0 [ERROR] $error_message"
    exit 1
fi

exit 0
