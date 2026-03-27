#!/bin/bash

set -e

dsn="$1"

# Verify that <PROJ>_SENTRY_PROJECT and <PROJ>_DSN point to the same project
if [ "$SENTRY_AUTH_TOKEN" == "" ]; then
    >&2 echo "$0 [ERROR] SENTRY_AUTH_TOKEN must be defined. See https://docs.sentry.io/product/cli/configuration/
        In GitHub Actions environment this means that corresponding secret is not set."
    exit 2
fi
api_response=$(curl https://sentry.io/api/0/projects/ \
    -H 'Authorization: Bearer '"$SENTRY_AUTH_TOKEN" 2>/dev/null)
id_slug=$(echo "$api_response" | grep -Eo '"id":"([^"]*)","slug":"(.*?)"' | sed 's/"id":"//g' | sed 's/","slug":"/ /g' | sed 's/"//g')

project_id_from_dsn=$(echo $dsn | cut -d / -f 4)

project_slug=$(echo "$id_slug" | grep $project_id_from_dsn | head -1 | cut -d ' ' -f 2)
if [ "$project_slug" == "" ]; then
    >&2 echo "$0 [ERROR] Unable to get project id using Sentry API. Wrong auth token? Response:"
    >&2 echo "$resp"
    exit 2
fi

echo $project_slug

exit 0
