#!/bin/bash

# Create release and upload sourcemaps to Sentry
# Must be run within project directory (e.g. './react/')

USAGE="Usage: ./sentry-release.sh ENV RELEASE"

set -e # exit immediately if any command exits with a non-zero status

# Parse and validate command-line arguments
env="$1"
release="$2"
if [[ "$env" == "" || "$release" == "" ]]; then
  echo "$0: [error] missing required command-line arguments."
  echo $USAGE
  exit 1
fi

proj=$(basename $(pwd))
    
if [ "$SENTRY_ORG" == "" ]; then
  echo "$0 [ERROR] SENTRY_ORG must be defined in ./env-config/$env.env."
  exit 1
fi
# sets $sentry_project var to the value of e.g. REACT_SENTRY_PROJECT from env-config/<env>.env
. get_proj_var.sh "%s_SENTRY_PROJECT" $proj
. get_proj_var.sh "%s_SOURCEMAPS_URL_PREFIX" $proj
. get_proj_var.sh "%s_SOURCEMAPS_DIR" $proj

sentry-cli releases -o $SENTRY_ORG new -p $sentry_project $release
sentry-cli releases -o $SENTRY_ORG finalize -p $sentry_project $release
sentry-cli releases -o $SENTRY_ORG -p $sentry_project set-commits --auto $release --ignore-missing
sentry-cli releases -o $SENTRY_ORG -p $sentry_project files $release upload-sourcemaps --url-prefix "$sourcemaps_url_prefix" --validate "$sourcemaps_dir" 
sentry-cli deploys -o $SENTRY_ORG new -p $sentry_project -r $release -e $env -n $env
