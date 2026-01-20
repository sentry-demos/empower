#!/bin/bash

set -e

gcloud run deploy $AGENT_CLOUD_RUN_SERVICE_NAME \
	--region $GCP_REGION \
	--source . \
	--platform managed \
	--allow-unauthenticated \
	--memory 512Mi \
	--cpu 1 \
	--min-instances 1 \
	--max-instances 1 \
    --set-env-vars AGENT_DSN=${AGENT_DSN} \
    --set-env-vars AGENT_SENTRY_ENVIRONMENT=${AGENT_SENTRY_ENVIRONMENT} \
    --set-env-vars API_HOST=0.0.0.0 \
    --set-env-vars API_RELOAD=false \
    --set-env-vars MAX_TOKENS=1000 \
    --set-env-vars MCP_URL=${MCP_URL} \
    --set-env-vars OPENAI_API_KEY=${AGENT_OPENAI_API_KEY} \
	# GCP sets $PORT automatically
