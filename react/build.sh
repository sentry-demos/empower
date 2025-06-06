#!/bin/bash

# Usage: ./build.sh

set -e # exit immediately if any command exits with a non-zero status

../bin/envsubst.sh < config-overrides.js.template > config-overrides.js

export SENTRY_RELEASE=$RELEASE

rm -rf build
# npm ci does not update minor versions ->
# (1) less chance of breaking (2) less noise in PR from package-lock.json
npm ci
npm run build # defined in 'scripts' in package.json
  
