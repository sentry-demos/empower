#!/bin/bash

USAGE="Usage: ./build.sh"

set -e # exit immediately if any command exits with a non-zero status

npm run build # defined in 'scripts' in package.json
