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
	--max-instances 1
