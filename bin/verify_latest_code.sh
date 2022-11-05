#!/bin/bash

# Outputs diff --stat between the current working tree and master branch of
# sentry-demos/application-monitoring

UPSTREAM_BRANCH="master"
UPSTREAM_URL="git@github.com:sentry-demos/application-monitoring-deploy.git"
ALT_UPSTREAM_URL="https://github.com/sentry-demos/application-monitoring-deploy.git"

remote=$(git remote -v | grep $UPSTREAM_URL | head -1 | cut -f 1)
if [ "$remote" == "" ]; then
  remote=$(git remote -v | grep $ALT_UPSTREAM_URL | head -1 | cut -f 1)
fi
if [ "$remote" == "" ]; then
  remote="deploy"
  git remote add $remote $UPSTREAM_URL >/dev/null
fi

git fetch $remote >/dev/null

git diff --stat $remote/$UPSTREAM_BRANCH -- ':!.github/workflows/auto-deploy.yml' ':!env-config/*.env'
git diff --stat $remote/$UPSTREAM_BRANCH:env-config/production.env env-config/production.env
