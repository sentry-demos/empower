#!/bin/bash

# Create release and upload sourcemaps to Sentry
# Must be run within project directory (e.g. './react/')

create_sentry_release() {
  local org="$1"                 # Organization slug
  local proj="$2"                # Project slug
  local release="$3"             # Release version
  local env="$4"                 # Environment
  local upload_sourcemaps="$5"   # Whether to upload sourcemaps
  local auth_token="$6"          # Sentry auth token

  . get_proj_var.sh "%s_SENTRY_PROJECT" "$proj"
  . get_proj_var.sh "%s_SOURCEMAPS_URL_PREFIX" "$proj"
  . get_proj_var.sh "%s_SOURCEMAPS_DIR" "$proj"

  sentry-cli releases -o "$org" new -p "$proj" "$release" --auth-token "$auth_token"
  sentry-cli releases -o "$org" finalize -p "$proj" "$release" --auth-token "$auth_token"
  sentry-cli releases -o "$org" -p "$proj" set-commits --auto "$release" --ignore-missing --auth-token "$auth_token"
  
  if [ "$upload_sourcemaps" == "true" ]; then
    sentry-cli releases -o "$org" -p "$proj" files "$release" upload-sourcemaps --url-prefix "$sourcemaps_url_prefix" --validate "$sourcemaps_dir" --auth-token "$auth_token"
  fi
  
  sentry-cli deploys -o "$org" new -p "$proj" -r "$release" -e "$env" -n "$env" --auth-token "$auth_token"
}


USAGE="Usage: ./sentry-release.sh ENV RELEASE UPLOAD_SOURCEMAPS MIRROR_TO_SANDBOX \
  UPLOAD_SOURCEMAPS = false | true \
  MIRROR_TO_SANDBOX = false | true"

set -e # exit immediately if any command exits with a non-zero status

echo "$0: Creating release and uploading source maps with sentry-cli..."

# Parse and validate command-line arguments
env="$1"
release="$2"
upload_sourcemaps="$3"
mirror_to_sandbox="$4"

if [[ "$env" == "" || "$release" == "" || "$upload_sourcemaps" == "" ]]; then
  echo "$0: [error] missing required command-line arguments."
  echo $USAGE
  exit 1
fi

proj=$(basename $(pwd))
    
create_sentry_release "$SENTRY_ORG" "$proj" "$release" "$env" "$upload_sourcemaps" "$SENTRY_AUTH_TOKEN"

if [ "$mirror_to_sandbox" == "true" ]; then
  create_sentry_release "$SENTRY_SANDBOX_ORG" "$proj" "$release" "$env" "$upload_sourcemaps" "$SENTRY_SANDBOX_AUTH_TOKEN"
fi