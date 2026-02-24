#!/bin/bash
# Deploy OTLP Collector to Cloud Run.
# Requires: OTLPCOLLECTOR_CLOUD_RUN_SERVICE, GCP_REGION, SENTRY_ORG, SENTRY_AUTH_TOKEN
# (source staging.env or set explicitly before running).
#
# Not implemented at this time: local.env, run_local.sh, production.env.

set -e

gcloud run deploy "$OTLPCOLLECTOR_CLOUD_RUN_SERVICE" \
	--region "$GCP_REGION" \
	--source . \
	--platform managed \
	--ingress=all \
	--allow-unauthenticated \
	--memory 512Mi \
	--cpu 1 \
	--min-instances 0 \
	--max-instances 10 \
	--set-env-vars "SENTRY_ORG=$SENTRY_ORG,SENTRY_AUTH_TOKEN=$SENTRY_AUTH_TOKEN"
