#!/bin/bash

# Usage: ./build.sh

set -e # exit immediately if any command exits with a non-zero status

rm -rf build
# npm ci does not update minor versions ->
# (1) less chance of breaking (2) less noise in PR from package-lock.json
npm ci 
# below avoids source map processing error in Sentry when stacktrace includes inline JS
export INLINE_RUNTIME_CHUNK=false
npm run build # defined in 'scripts' in package.json

cp ./serve.json build/serve.json