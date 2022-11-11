#!/bin/bash

set -e

diff="$(source_diff_upstream.sh)"

if [ "$diff" != "" ]; then
    echo "You are about to do a deployment to production, but current code is different from HEAD at
    sentry-demos/application-monitoring AND/OR your production.env is different from production.env in 
    sentry-demos/application-monitoring-deploy:"
    MAX_DIFF_LINES="7"
    difflines="$(echo "$diff" | wc -l)"
    diff="$(echo -n "$diff" | head -$MAX_DIFF_LINES)"
    echo "$diff"
    if [ "$difflines" -gt "$MAX_DIFF_LINES" ]; then
        echo " ... ($((difflines - $MAX_DIFF_LINES)) more lines)"
    fi
    phrase="yes, deploy to production"
    read -p "Type '$phrase' to continue... " choice
    if [ "$choice" != "$phrase" ]; then
        echo "Exiting without performing command."
        exit 1
    fi
fi