#!/bin/bash
# Reset the self-heal demo after a run (or an aborted one):
#   1. close open agent PRs and delete their branches
#   2. resolve open selfheal-flask issues, so the next break is a fresh alert
#   3. put the bug back and redeploy (arm.sh)
# Needs: gh (signed in with merge rights), SENTRY_AUTH_TOKEN (project:write).
set -euo pipefail

REPO=${SELFHEAL_REPO:-sentry-demos/empower}
SENTRY_ORG=${SENTRY_ORG:-demo}
SENTRY_PROJECT=selfheal-flask
SENTRY_URL=${SENTRY_URL:-https://sentry.io}

echo "Closing open agent PRs..."
gh pr list --repo "$REPO" --base selfheal/base --label selfheal-agent --state open --json number --jq '.[].number' |
  while read -r pr; do
    gh pr close "$pr" --repo "$REPO" --delete-branch --comment "Closed by selfheal/scripts/reset.sh"
  done

if [ -n "${SENTRY_AUTH_TOKEN:-}" ]; then
  echo "Resolving unresolved $SENTRY_PROJECT issues..."
  curl -sf -X PUT \
    -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" -H 'Content-Type: application/json' \
    --data '{"status":"resolved"}' \
    "$SENTRY_URL/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/issues/?status=unresolved" > /dev/null
else
  echo "SENTRY_AUTH_TOKEN not set; skipping issue resolution"
fi

"$(dirname "$0")/arm.sh"
