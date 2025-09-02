#!/bin/bash

# Usage: 
# . get_proj_var ENV_VAR_FORMAT SUBST ... 
#
# ENV_VAR_FORMAT is a printf-style string with one or more '%s' subsitutions, e.g. for project name
#
# Example:
# . get_proj_var %s_APP_%s_BACKEND react spring-boot
# 
# Defines an "output" variable named 'app_backend' (i.e. printf string with '%s' and extra underscored removed) and
# sets its value to the value of REACT_APP_BACKEND_URL_SPRINGBOOT that is _already_ set in the current shell
# (presumably from env-config/*.env)
#
# Output variable name is determine magically as follows: MY_%s_VAR_NAME_%s -> my_var_name
#
# Meant to be sourced, not called, so that calling script has access to variable
# '. get_proj_var.sh' is the same as 'source get_proj_var.sh'

set -e

_top=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

_env_var_format="$1"

_env_var_name=$($_top/var_name.sh $@)
if [ "${!_env_var_name}" == "" ]; then
    >&2 echo "$0: [error] ${_env_var_name} must be defined in ./env-config/*.env"
    exit 1
fi
# --> magic <--
_output_var_name=$(echo $_env_var_format | sed -r 's/(%s_|_%s)//g')
_output_var_name=$(echo $_output_var_name | tr '[:upper:]' '[:lower:]')
printf -v "$_output_var_name" "%s" "${!_env_var_name}"

unset _top _env_var_format _env_var_name _output_var_name
