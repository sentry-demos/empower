#!/bin/bash

set -e

# Outputs diff --stat between the current working tree and master branch of
# sentry-demos/application-monitoring

UPSTREAM_BRANCH="master"
UPSTREAM_URL="git@github.com:sentry-demos/application-monitoring.git"
CONFIG_BRANCH="main"
CONFIG_URL="git@github.com:sentry-demos/application-monitoring-config.git"

upstream_remote=$(git remote -v | grep $UPSTREAM_URL | head -1 | cut -f 1)
if [ "$upstream_remote" == "" ]; then
  upstream_remote="deploy-upstream"
  git remote add $upstream_remote $UPSTREAM_URL >/dev/null
fi

config_remote=$(git remote -v | grep $CONFIG_URL | head -1 | cut -f 1)
if [ "$config_remote" == "" ]; then
  config_remote="deploy-config"
  git remote add $config_remote $CONFIG_URL >/dev/null
fi

git fetch $upstream_remote >/dev/null
git fetch $config_remote >/dev/null

git diff --stat $upstream_remote/$UPSTREAM_BRANCH -- ':!env-config/*.env'
git diff --stat $config_remote/$CONFIG_BRANCH:production.env env-config/production.env
