#!/bin/bash

set -e

# Outputs diff --stat between the current working tree and master branch of sentry-demos/empower

UPSTREAM_BRANCH="master"
UPSTREAM_URL="git@github.com:sentry-demos/empower.git"

upstream_remote=$(git remote -v | grep $UPSTREAM_URL | head -1 | cut -f 1)
if [ "$upstream_remote" == "" ]; then
  upstream_remote="deploy-upstream"
  git remote add $upstream_remote $UPSTREAM_URL >/dev/null
fi

git fetch $upstream_remote >/dev/null

git diff --stat $upstream_remote/$UPSTREAM_BRANCH -- ':!env-config/*.env'
