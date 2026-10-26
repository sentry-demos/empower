#!/bin/bash
# Deploy the webhook receiver to Cloud Run. Secrets come from Secret Manager:
#   SELFHEAL_SENTRY_CLIENT_SECRET - the internal integration's client secret
#   SELFHEAL_GITHUB_TOKEN         - bot token that can trigger repository_dispatch
# min-instances=1 keeps it always on, so the first alert of a demo isn't a cold start.
set -euo pipefail

GCP_PROJECT=${GCP_PROJECT:-sales-engineering-sf}
GCP_REGION=${GCP_REGION:-us-central1}
SERVICE=${SERVICE:-selfheal-receiver}

cd "$(dirname "$0")"
gcloud run deploy "$SERVICE" \
  --project "$GCP_PROJECT" \
  --region "$GCP_REGION" \
  --source . \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 2 \
  --set-env-vars "GITHUB_REPO=${GITHUB_REPO:-sentry-demos/empower},BASE_BRANCH=selfheal/base" \
  --set-secrets "SENTRY_CLIENT_SECRET=SELFHEAL_SENTRY_CLIENT_SECRET:latest,GITHUB_TOKEN=SELFHEAL_GITHUB_TOKEN:latest"

echo "Webhook URL for the Sentry internal integration:"
echo "  $(gcloud run services describe "$SERVICE" --project "$GCP_PROJECT" --region "$GCP_REGION" --format 'value(status.url)')/sentry"
