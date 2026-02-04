#!/bin/bash

set -e

gcloud run deploy $MCP_CLOUD_RUN_SERVICE \
	--region $GCP_REGION \
	--source . \
	--platform managed \
	--allow-unauthenticated \
	--memory 512Mi \
	--cpu 1 \
	--min-instances 1 \
	--max-instances 1
