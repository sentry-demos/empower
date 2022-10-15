#!/bin/bash

# Usage: 
# ./var_name.sh ENV_VAR_FORMAT SUBST ... 
#
# ENV_VAR_FORMAT is a printf-style string with one or more '%s' subsitutions, e.g. for project name
#
# Example:
# ./var_name.sh %s_APP_%s_BACKEND react spring-boot
# REACT_APP_SPRINGBOOT_BACKEND

set -e

env_var_format="$1"
substs="${@:2}"
if [[ $# < 2 ]]; then
    echo "$0: [error] missing arguments"
    echo "Usage: ./var_name.sh ENV_VAR_FORMAT SUBST ..."
fi
if [[ ! $env_var_format = *%s* ]]; then
    # TODO: validate number of placeholders matches number of command arguments - 1
    echo "$0: [error] ENV_VAR_FORMAT must contain at least 1 printf-style substitution placeholder '%s'."
    echo "Usage example: ./var_name.sh %s_SENTRY_PROJECT react"
fi

substs_upper_no_dashes=$(echo ${substs//-/} | tr '[:lower:]' '[:upper:]')
env_var_name=$(printf "$env_var_format" $substs_upper_no_dashes) # bash only

echo $env_var_name