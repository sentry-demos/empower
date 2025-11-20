#!/bin/bash
set -e

PROJECT_ID=sales-engineering-sf
PREFIX=""
PASS_MODE=0
secrets=()

# ./_bin/gcp_secret_wrapper.sh [--prefix=PREFIX] [--pass] [MY_SECRET_1 MY_SECRET_2] -- <the actual command>
# 
# With --pass flag, the script will not error if no secrets are provided and will just execute the command after --

# Function to get access token from gcloud or Metadata Server
get_access_token() {
  if command -v gcloud &> /dev/null; then
    gcloud auth print-access-token
  else
    curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token |
    sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p'
  fi
}

# Function to get secret from Secret Manager using curl and sed
get_secret() {
  local secret_name="$1"
  local access_token=$(get_access_token)
  #local project_id=$(get_project_id) # Using Metadata Server for project ID (unused)

  if [ -z "$access_token" ]; then
    echo "[ERROR] $0: Failed to get access token" >&2
    exit 1
  fi

  # Get the JSON response and convert newlines to a special character
  local response=$(curl -s -X GET \
    -H "Authorization: Bearer $access_token" \
    -H "Content-Type: application/json; charset=utf-8" \
    "https://secretmanager.googleapis.com/v1/projects/$PROJECT_ID/secrets/$secret_name/versions/latest:access" | tr '\n' ' ')

  # Extract the data field using parameter expansion
  local data="${response#*\"data\": \"}"
  data="${data%%\"*}"

  # Check for errors or empty data
  if [[ "$response" == *"\"error\": {"* || -z "$data" ]]; then
    echo "[ERROR] $0: Secret '$secret_name' is missing from project '$PROJECT_ID'" >&2
    exit 1
  fi

  # Convert back to newlines and decode the base64 data
  echo "$data" | base64 --decode
}

# This can be used on a GAE VM to get project ID. But we are now only running this locally.
#get_project_id() {
#  curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/project/project-id
#}

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix=*)
      PREFIX="${1#*=}"
      shift
      ;;
    --pass)
      PASS_MODE=1
      shift
      ;;
    --)
      shift
      break
      ;;
    *)
      if [[ -n "$1" ]]; then
        secrets+=("$1")
      fi
      shift
      ;;
  esac
done

# Set environment variables for each secret (only if not in pass mode or if secrets exist)
if [ $PASS_MODE -eq 0 ] || [ ${#secrets[@]} -gt 0 ]; then
  for secret_name in "${secrets[@]}"; do
    secret_value=$(get_secret "$secret_name")
    export "$PREFIX$secret_name"="$secret_value"
  done
fi

# Execute the main application with the remaining arguments
exec "$@"
