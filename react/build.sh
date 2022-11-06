#!/bin/bash

# Usage: ./build.sh

set -e # exit immediately if any command exits with a non-zero status

rm -rf build
npm install
npm run build # defined in 'scripts' in package.json
