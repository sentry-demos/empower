#!/bin/bash

# Variable can be either defined in .env file
# or in the shell when calling command, e.g.:
#
# REACT_APP_MY_VAR=foobar npm run build
# 
# Names must be prefixed with 'REACT_APP_', otherwise they will not show up
#
# See https://create-react-app.dev/docs/adding-custom-environment-variables

set -e # exit immediately if any command exits with a non-zero status

if [ -f .env ]; then
  source .env
fi

if [ ! -f validate_env.list ]; then
  echo "$0: ERROR: validate_env.list file does not exist in current directory: $(pwd)"
  exit 1
fi

while read var || [[ -n $var ]]; do # won't skip last line if missing line break
  if [[ $var = \#* || $var = *[[:space:]]* ]]; then # ignore comments and empty lines
    continue
  fi
  var=$(echo "$var" | xargs) # trim whitespace

  # Other possible methods:
  #   value=$(printenv $var)
  #   match=$(grep -e "^$var=" .env | cut -d '=' -f 2)
  
  # Note this relies on 'source .env' above
  # but will also work with exported variables 
  value="${!var}" # won't work in zsh, only bash

  if [ "$value" == "" ]; then
    >&2 echo "validate_env.sh: [ERROR] required env variable $var not defined or has empty value." \
             "You must add it to your env-config/*.env file." 
    exit 1
  else
    echo "validate_env.sh: verified $var is set."
  fi
done < validate_env.list

