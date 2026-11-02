#!/bin/bash
# Deploy the webhook receiver to Cloud Run. Secrets come from Secret Manager:
#   SELFHEAL_SENTRY_CLIENT_SECRET       - the default org's (demo) `selfheal` integration client secret
#   SELFHEAL_SENTRY_CLIENT_SECRET_<ORG> - each extra org's, e.g. SELFHEAL_SENTRY_CLIENT_SECRET_TEAM_SE
#   SELFHEAL_GITHUB_APP_PRIVATE_KEY     - the GitHub App's private key (.pem), for creating run branches
# and the app's numeric ID is passed in GITHUB_APP_ID:
#   GITHUB_APP_ID=123456 selfheal/receiver/deploy.sh
#
# EXTRA_ORGS lists the other Sentry orgs (default "team-se"); their targets are in selfheal/targets.json.
# Fallback without an app: GITHUB_AUTH=token uses a token from secret SELFHEAL_GITHUB_TOKEN.
# min-instances=1 keeps it always on, so the first alert of a demo isn't a cold start.
set -euo pipefail

GCP_PROJECT=${GCP_PROJECT:-sales-engineering-sf}
GCP_REGION=${GCP_REGION:-us-central1}
SERVICE=${SERVICE:-selfheal-receiver}
GITHUB_AUTH=${GITHUB_AUTH:-app}
EXTRA_ORGS=${EXTRA_ORGS:-team-se}

env_vars="GITHUB_REPO=${GITHUB_REPO:-sentry-demos/empower},BASE_BRANCH=selfheal/base"
secrets="SENTRY_CLIENT_SECRET=SELFHEAL_SENTRY_CLIENT_SECRET:latest"
for org in $EXTRA_ORGS; do
  suffix=$(echo "$org" | tr '[:lower:]-' '[:upper:]_')   # team-se -> TEAM_SE
  secrets="$secrets,SENTRY_CLIENT_SECRET_$suffix=SELFHEAL_SENTRY_CLIENT_SECRET_$suffix:latest"
done
if [ "$GITHUB_AUTH" = "app" ]; then
  : "${GITHUB_APP_ID:?Set GITHUB_APP_ID to the GitHub App ID, or use GITHUB_AUTH=token}"
  env_vars="$env_vars,GITHUB_APP_ID=$GITHUB_APP_ID"
  secrets="$secrets,GITHUB_APP_PRIVATE_KEY=SELFHEAL_GITHUB_APP_PRIVATE_KEY:latest"
else
  secrets="$secrets,GITHUB_TOKEN=SELFHEAL_GITHUB_TOKEN:latest"
fi

cd "$(dirname "$0")"
# The receiver routes alerts with the same targets file the runner uses
cp ../targets.json targets.json
trap 'rm -f targets.json' EXIT

gcloud run deploy "$SERVICE" \
  --project "$GCP_PROJECT" \
  --region "$GCP_REGION" \
  --source . \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 2 \
  --set-env-vars "$env_vars" \
  --set-secrets "$secrets"

echo "Webhook URL for the Sentry internal integration (use it in every org):"
echo "  $(gcloud run services describe "$SERVICE" --project "$GCP_PROJECT" --region "$GCP_REGION" --format 'value(status.url)')/sentry"
