#!/bin/bash

# Checks if all variables listed in <current dir>/validate_env.sh are present
# in the current shell environment (i.e. exported)
# Additionally, verifies that Sentry project slug and DSN match.
#
# Must be run from within project dir (e.g. './react/')

set -e # exit immediately if any command exits with a non-zero status

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
  
  value="${!var}" # won't work in zsh, only bash

  if [ "$value" == "" ]; then
    >&2 echo "$0: [ERROR] required env variable $var not defined or has empty value." \
            "You must add it to your env-config/*.env file." 
    exit 1
  fi
done < validate_env.list
  
proj=$(basename $(pwd))
. get_proj_var.sh "%s_APP_DSN" $proj
. get_proj_var.sh "%s_SENTRY_PROJECT" $proj
error_message=$(var_name.sh "%s_SENTRY_PROJECT and %s_APP_DSN point to different projects." $proj $proj)
validate_dsn.sh $sentry_project $app_dsn $error_message
