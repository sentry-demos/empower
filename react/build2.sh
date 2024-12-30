#!/bin/bash

# Usage: ./build.sh

set -e # exit immediately if any command exits with a non-zero status

envsubst < config-overrides.js.template > config-overrides.js

rm -rf build
npm run build # defined in 'scripts' in package.json
  
