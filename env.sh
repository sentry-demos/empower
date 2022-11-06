#!/bin/bash

# Usage: ../env.sh env [command ...]
#
# Must be run from inside project dir (e.g. './react/')
#
# There are two modes in which this script can be run. Both will create a temporary
# .env file in current directory by copying env-config/*.env, augment it with RELEASE
# (if not already set in env-config) and validate it using 'validate_env.list'.
#
# In the first mode (called from deploy.sh with 1 arg) it won't do anything else.
# Example:
#   ../env.sh production
#
# In the second mode (standalone), when given more than one arg, it will additionally
# run 2nd arg and the rest as command. Once the command exits it will clean up .env.
# Example:
#   ../env.sh local npm start

set -e

env=$1
proj=$(basename $(pwd))

if [ ! -f "../env-config/$env.env" ]; then
  echo "[ERROR] Missing file env-config/$env.env or invalid environment '$env'."
  exit 1
fi
if [ -f ".env" ]; then
    echo "[ERROR] project '$proj' contains legacy .env file that is no longer used. Please delete this file,
    it is no longer needed and has been replaced by ./env-config/*.env. Note that this error
    might also happen if deploy.sh or env.sh failed to clean up the .env file it has generated dynamically 
    during an earlier run."
    exit 1
fi
if [ "$2" != "" ]; then
    export PATH="$PATH:../bin"
fi

cp ../env-config/$env.env .env

function cleanup {
    rm -f .env
}
trap cleanup EXIT # if fails while running this script or while running command

# You can specify RELEASE in env-config/*.env
# Otherwise this script will generate one using this format:
# <PROJ>_RELEASE_PACKAGE_NAME@<CALENDAR VERSION>

echo "" >> .env # in case no newline
# source .env will not work because of '$' symbols in values (PASSWORD)
unset RELEASE # so we don't accidentally pick up RELEASE from another project (deploy.sh)
export $(grep -v '^#' .env | xargs) # just for *_RELEASE_PACKAGE_NAME and RELEASE
if [ "$RELEASE" == "" ]; then
    . get_proj_var.sh "%s_RELEASE_PACKAGE_NAME" $proj
    release="${release_package_name}@"`release.sh`
    >&2 echo $release
    # deploy.sh script itself and non-React projects expect RELEASE
    echo "RELEASE=$release" >> .env
    export RELEASE="$release"
fi
if [ "$proj" == "react" ]; then
    echo "REACT_APP_RELEASE=$RELEASE" >> .env
fi

if [ "$2" == "" ]; then 
    # Called from deploy.sh
    #
    # 1. Calling script will use .env, this script doen't have control over that.
    # For that reason we pass it down to the calling script so it can clean up later.
    # 2. We can't export variables into calling script, so the calling script is
    # also responsible for that (not required for projects using dotenv package).
    trap - EXIT
    echo "$(pwd)/.env" 
else
    # Standalone mode

    export $(grep -v '^#' .env | xargs) # in case project doesn't use dotenv

    if [ "$proj" == "react" ]; then
        # avoids error npm start tries to bind to every available network interface
        HOST=localhost "${@:2}"
    else
        "${@:2}"
    fi
fi
