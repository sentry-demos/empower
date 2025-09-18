#!/bin/bash

# Create release in Sentry

USAGE="Usage: ./sentry-release.sh ENVIRONMENT SENTRY_ORG SENTRY_PROJECT RELEASE"

set -e

echo "$0: Creating release with sentry-cli..."

# Parse and validate command-line arguments
env="$1"
sentry_org="$2"
sentry_project="$3"
release="$4"

if [[ "$env" == "" || "$sentry_org" == "" || "$sentry_project" == "" || "$release" == "" ]]; then
  echo "$0: [error] missing required command-line arguments."
  echo $USAGE
  exit 1
fi

sentry-cli releases -o $sentry_org new -p $sentry_project $release
sentry-cli releases -o $sentry_org finalize -p $sentry_project $release
sentry-cli releases -o $sentry_org -p $sentry_project set-commits --auto $release --ignore-missing
sentry-cli deploys -o $sentry_org new -p $sentry_project -r $release -e $env -n $env
