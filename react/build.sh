#!/bin/bash

# Usage: ./build.sh RELEASE

set -e # exit immediately if any command exits with a non-zero status

if [ "$1" == "" ]; then
  echo "$0 [ERROR]: missing RELEASE argument."
  exit 1
fi
export REACT_APP_RELEASE="$1" # create-react-app requires all env vars start with REACT_APP_

npm run build # defined in 'scripts' in package.json
