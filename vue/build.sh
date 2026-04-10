#!/bin/bash

USAGE="Usage: ./build.sh"

set -e # exit immediately if any command exits with a non-zero status

# Export SENTRY_RELEASE for Sentry integration
export SENTRY_RELEASE=$VUE_RELEASE

rm -rf dist
npm install
npm run build # defined in 'scripts' in package.json

sentry-release.sh ${VUE_ENVIRONMENT} ${SENTRY_ORG} ${VUE_SENTRY_PROJECT} ${VUE_RELEASE}
sentry-cli sourcemaps upload -o ${SENTRY_ORG} -p ${VUE_SENTRY_PROJECT} --release ${VUE_RELEASE} --url-prefix ~/assets --validate dist/assets

# Create serve configuration with profiling headers in the current directory
cat > serve.json << EOF
{
  "headers": [
    {
      "source": "**/*",
      "headers": [
        {
          "key": "Document-Policy",
          "value": "js-profiling"
        }
      ]
    }
  ]
}
EOF
