#!/bin/bash

set -e

gcloud run deploy $AGENT_CLOUD_RUN_SERVICE_NAME \
	--source . \
	--platform managed \
	--allow-unauthenticated \
	--memory 512Mi \
	--cpu 1 \
	--min-instances 1 \
	--max-instances 1 \
	--set-env-vars AGENT_OPENAI_API_KEY=$AGENT_OPENAI_API_KEY \
	--set-env-vars AGENT_DSN=$AGENT_DSN \
	--set-env-vars AGENT_SENTRY_ENVIRONMENT=$AGENT_SENTRY_ENVIRONMENT \
	--set-env-vars API_PORT=8000
