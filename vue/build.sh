#!/bin/bash

USAGE="Usage: ./build.sh"

set -e # exit immediately if any command exits with a non-zero status

# Export SENTRY_RELEASE for Sentry integration
export SENTRY_RELEASE=$RELEASE

rm -rf dist
npm install
npm run build # defined in 'scripts' in package.json

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
