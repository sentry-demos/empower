#!/bin/bash
# Deploy the webhook receiver to Cloud Run. Secrets come from Secret Manager:
#   SELFHEAL_SENTRY_CLIENT_SECRET     - the `selfheal` internal integration's client secret
#   SELFHEAL_GITHUB_APP_PRIVATE_KEY   - the GitHub App's private key (.pem), for creating run branches
# and the app's numeric ID is passed in GITHUB_APP_ID:
#   GITHUB_APP_ID=123456 selfheal/receiver/deploy.sh
#
# Fallback without an app: GITHUB_AUTH=token uses a token from secret SELFHEAL_GITHUB_TOKEN.
# min-instances=1 keeps it always on, so the first alert of a demo isn't a cold start.
set -euo pipefail

GCP_PROJECT=${GCP_PROJECT:-sales-engineering-sf}
GCP_REGION=${GCP_REGION:-us-central1}
SERVICE=${SERVICE:-selfheal-receiver}
GITHUB_AUTH=${GITHUB_AUTH:-app}

env_vars="GITHUB_REPO=${GITHUB_REPO:-sentry-demos/empower},BASE_BRANCH=selfheal/base"
secrets="SENTRY_CLIENT_SECRET=SELFHEAL_SENTRY_CLIENT_SECRET:latest"
if [ "$GITHUB_AUTH" = "app" ]; then
  : "${GITHUB_APP_ID:?Set GITHUB_APP_ID to the GitHub App ID, or use GITHUB_AUTH=token}"
  env_vars="$env_vars,GITHUB_APP_ID=$GITHUB_APP_ID"
  secrets="$secrets,GITHUB_APP_PRIVATE_KEY=SELFHEAL_GITHUB_APP_PRIVATE_KEY:latest"
else
  secrets="$secrets,GITHUB_TOKEN=SELFHEAL_GITHUB_TOKEN:latest"
fi

cd "$(dirname "$0")"
gcloud run deploy "$SERVICE" \
  --project "$GCP_PROJECT" \
  --region "$GCP_REGION" \
  --source . \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 2 \
  --set-env-vars "$env_vars" \
  --set-secrets "$secrets"

echo "Webhook URL for the Sentry internal integration:"
echo "  $(gcloud run services describe "$SERVICE" --project "$GCP_PROJECT" --region "$GCP_REGION" --format 'value(status.url)')/sentry"
