#!/bin/bash

# Usage: ./build.sh

set -e # exit immediately if any command exits with a non-zero status

rm -rf build
# npm ci or yarn install --frozen-lockfile does not update minor versions ->
# (1) less chance of breaking (2) less noise in PR from package-lock.json or yarn.lock
yarn install --frozen-lockfile
yarn run build # defined in 'scripts' in package.json
