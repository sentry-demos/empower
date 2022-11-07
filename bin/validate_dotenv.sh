#!/bin/bash

# Variables must be defined in .env file, not current shell. Exports into current
# shell work with run.sh but won't be carried over to GCloud runtime environment.
#
# For React specifically:
#
#   REACT_APP_MY_VAR=foobar npm run build
# 
#   Names must be prefixed with 'REACT_APP_', otherwise they will not show up
#
#   See https://create-react-app.dev/docs/adding-custom-environment-variables

set -e # exit immediately if any command exits with a non-zero status
  
if [ ! -f .env ]; then
    echo "$0: ERROR: .env does not exist in current directory: $(pwd). It should have been
    created by 'parent' script."
    exit 1
fi

env -i PATH="$PATH" SENTRY_AUTH_TOKEN="$SENTRY_AUTH_TOKEN" /bin/bash -c 'export $(grep -v ^# .env | xargs); validate_env.sh'
 