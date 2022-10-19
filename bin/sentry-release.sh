#!/bin/bash

USAGE="Usage: ./sentry-release.sh SENTRY_ORG SENTRY_PROJECT ENVIRONMENT RELEASE SOURCEMAPS_URL_PREFIX SOURCEMAPS_DIR"

set -e # exit immediately if any command exits with a non-zero status

# Parse and validate command-line arguments
sentry_org="$1"
sentry_project="$2"
environment="$3"
release="$4"
sourcemaps_url_prefix="$5"
sourcemaps_dir="$6"
if [[ "$sentry_org" == "" || "$sentry_project" == "" || "$environment" == "" || "$release" == "" \
      || "$sourcemaps_url_prefix" == "" || "$sourcemaps_dir" == "" ]]; then
  echo "build_and_upload_sourcemaps.sh: [error] missing required command-line arguments."
  echo $USAGE
  exit 1
fi

sentry-cli releases -o $sentry_org new -p $sentry_project $release
sentry-cli releases -o $sentry_org finalize -p $sentry_project $release
sentry-cli releases -o $sentry_org -p $sentry_project set-commits --auto $release --ignore-missing
sentry-cli releases -o $sentry_org -p $sentry_project files $release upload-sourcemaps --url-prefix "$sourcemaps_url_prefix" --validate "$sourcemaps_dir" 
sentry-cli deploys -o $sentry_org new -p $sentry_project -r $release -e $environment -n $environment
