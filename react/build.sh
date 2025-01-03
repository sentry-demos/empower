#!/bin/bash

# Usage: ./build.sh

set -e # exit immediately if any command exits with a non-zero status

envsubst < config-overrides.js.template > config-overrides.js

rm -rf build
# npm ci does not update minor versions ->
# (1) less chance of breaking (2) less noise in PR from package-lock.json
npm ci
CI=false npm run build # defined in 'scripts' in package.json
  
