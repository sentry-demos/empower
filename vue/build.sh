#!/bin/bash

USAGE="Usage: ./build.sh"

set -e # exit immediately if any command exits with a non-zero status

rm -rf dist
npm install
npm run build # defined in 'scripts' in package.json

sentry-release.sh ${VUE_ENVIRONMENT} ${SENTRY_ORG} ${VUE_SENTRY_PROJECT} ${VUE_RELEASE}
sentry-cli sourcemaps upload -o ${SENTRY_ORG} -p ${VUE_SENTRY_PROJECT} --release ${VUE_RELEASE} --url-prefix ~/assets --validate dist/assets