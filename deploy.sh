#!/bin/bash

# deploy.sh - build, upload sourcemaps, and deploy or run locally any one or multiple projects
# using ./env-config/*.env for both build-time and runtime environment configuration. Must be
# called with --env parameter that specifies which env-config file to use. A special case is
# --env=local which will run each project's 'run.sh' script instead of deploying to Google App
# Engine (default). 
# 
# Usage: ./deploy.sh react flask --env=staging
#
# Can be run from any directory. In --env=local mode it will start web servers for ALL projects
# specified on command-line (backends first) and then eventually, upon exit (Ctrl+C), every one 
# of them. An error anywhere in the script (e.g. failed deployment or sentry-cli call) should 
# make the entire script exit immediately.
#
# All variables in *.env are passed into each projects runtime environment. 
# Some variables, however, are special and are additionally used during the build:
# 
#   SENTRY_ORG is passed to ./build_and_upload_sourcemaps.sh and used to specify which Sentry
#   org to create release in.
#
#   <PROJECT>_SENTRY_PROJECT is passed to ./build_and_upload_sourcemaps.sh and used to specify 
#   which Sentry project to create release in. 
# 
#   <PROJECT>_RELEASE_PACKAGE_NAME is used to create a new Sentry release (prepended to calendar
#   version e.g. 'package-name@22.9.5' )
#
#   <PROJECT>_SOURCEMAPS_URL_PREFIX 
#
#   <PROJECT>_SOURCEMAPS_DIR
#
#   <PROJECT>_APP_ENGINE_SERVICE is used to parametrize app.yaml.template for that project and
#   points to the Google App Engine (GAE) "service" to which the project should be deployed.
#   These values should be configured once in production.env and staging.env and never changed
#   again. Obviously, for local.env they are meaningless and not required.
#   e.g.: REACT_APP_ENGINE_SERVICE
# 
#   REACT_APP_<PROJECT>_BACKEND besides being passed into React application runtime these are
#   substituted with the values of respective REACT_APP_<PROJECT>_BACKEND_LOCAL when --env=local 
#   AND <PROJECT> is included in the list of projects to build from command-line arguments.
#    
# MIGRATION NOTE: 
#
#   The old .env and app.yaml must now be deleted from ./<project>/ directory. Instead move all the 
#   variables to ./env-config/<env>.env and create ./<project>/app.yaml.template with '<SERVICE>' placeholder
#   in place of actual service name. Finally add <PROJECT>_APP_ENGINE_SERVICE=<actual service name> to all the 
#   ./env-config/<env>.env files.

set -e # exit immediately if any command exits with a non-zero status
# https://fvue.nl/wiki/Bash:_Error_handling

# use top-level directory (repository root), to ensure this works regardless of current directory
top=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PATH="$PATH:$top/bin"

# Parse CLI arguments
projects=""
env=""
for arg in "$@"; do
  if [[ $arg = --env=* ]]; then
    env=$(echo $arg | cut -d '=' -f 2)
    echo "env = $env"
  else 
    projects="$projects $arg"
  fi
done

USAGE="[ERROR] Invalid arguments. Usage e.g.: ./deploy.sh --env=staging react flask"

# Validate CLI arguments
if [[ "$env" == "" || "$projects" == "" ]]; then
  echo "$USAGE"; 
  exit 1
fi

# Validate using latest code if --env=production
if [ -t 0 ] ; then
  # shell is interactive
  if [ "$env" == "production" ]; then
    echo "Verifying that the code in the current git working tree, branch and fork is identical
         to the default branch of upstream repository (sentry-demos/application-monitoring)..."
    diff="$(verify_latest_code.sh | head -3)"
    if [ "$diff" != "" ]; then
      echo "You are about to deploy to production, but current code is different from HEAD at sentry-demos:"
      echo "$diff"
      echo "..."
      phrase="yes deploy to production"
      read -p "Type '$phrase' to continue... " choice
      if [ "$choice" != "$phrase" ]; then
          echo "Exiting without performing command."
          exit 1
      else
        :
        #TODO email team
        # https://docs.sendgrid.com/for-developers/sending-email/api-getting-started
      fi
    fi
  fi
fi

# Re-order so backends are launched first
be_projects=""
fe_projects=""
for proj in $projects; do
  if [[ $proj =~ ^(flask|express|ruby|spring-boot)$ ]]; then
    be_projects+="$proj "
  else
    fe_projects+="$proj "
  fi
done
projects="$be_projects $fe_projects"

function cleanup { 
  for pid in $run_sh_pids; do
    # each run.sh has it's own cleanup function
    kill $pid 2>/dev/null
  done 
  rm -f $top/*/.app.yaml
  if [ "$generated_envs" != "" ]; then
    rm -f $generated_envs # bash only (passed as separate args) 
  fi
}
trap cleanup EXIT

run_sh_pids=""

for proj in $projects; do # bash only
  # Validate configuration files
  if [ ! -d $top/$proj ]; then
    echo "[ERROR] Project '$proj' does not exist"
    exit 1
  fi
  if [ ! -f "$top/env-config/$env.env" ]; then
    echo "[ERROR] Missing file ./env-config/$env.env"
    exit 1
  elif [ -f "$top/$proj/app.yaml" ]; then 
    echo "[ERROR] project '$proj' contains app.yaml file that is no longer used. Please delete this file,
    it is no longer be needed and has been replaced by app.yaml.template."
    exit 1
  elif [ -f "$top/$proj/.env" ]; then
    echo "[ERROR] project '$proj' contains .env file that is no longer used. Please delete this file,
    it is no longer needed and has been replaced by ./env-config/*.env. Note that this error
    might also happen if deploy.sh failed to clean up the .env file it has generated dynamically during
    an earlier run."
    # we make sure not to delete any pre-existing .env files during cleanup, see 'generated_envs'
    exit 1
  elif [ ! -f "$top/$proj/app.yaml.template" ]; then
    echo "[ERROR] Missing ./$proj/app.yaml.template with '<SERVICE>' placeholder in place of actual service name."
    exit 1
  fi

  # Export environment variables from ./env-config/<env>.env
  # Some projects still rely on .env so we generate it dynamicaly later down the road
  while read line || [[ -n $line ]]; do # won't skip last line if missing line break
    if [[ ! $line = \#* && $line = *[![:space:]]* ]]; then # ignore comments and empty lines
      export "$line"
    fi
  done < $top/env-config/$env.env

  if [[ "$env" == "local" && "$fe_projects" = *"$proj "* ]]; then 
    # Point to local backend http://host:port instead of cloud endpoints for all built BE projects
    # If no backend projects specified in CLI args, keep using cloud (production or staging) BE endpoints.
    for be_proj in $be_projects; do
      backend_var=$(var_name.sh %s_APP_%s_BACKEND $proj $be_proj)
      . get_proj_var.sh "%s_APP_%s_BACKEND_LOCAL" $proj $be_proj # sets $app_backend_local
      export "$backend_var=$app_backend_local"
    done 
  fi
  
  cd $top/$proj

  # *** BUILD ***
  . get_proj_var.sh "%s_RELEASE_PACKAGE_NAME" $proj
  release="${release_package_name}@"`release.sh`
  echo $release
  # Existing behavior in react build. TODO: is this necessary?
  if [ "$env" == "local" ]; then
    rm -rf build
    npm install
  fi
  export RELEASE="$release"
  ./build.sh "$release"

  # *** CREATE RELEASE AND UPLOAD SOURCEMAPS ***
  if [[ "$fe_projects" = *"$proj "* ]]; then # current project is frontend
    # We don't create releases for backend projects because it's not part of demo flow and sourcemaps are not
    # necessary either. 
    if [ "$SENTRY_ORG" == "" ]; then
      echo "$0 [ERROR] SENTRY_ORG must be defined in ./env-config/$env.env."
      exit 1
    fi
    # sets $sentry_project var to the value of e.g. REACT_SENTRY_PROJECT from env-config/<env>.env
    . get_proj_var.sh "%s_SENTRY_PROJECT" $proj
    . get_proj_var.sh "%s_SOURCEMAPS_URL_PREFIX" $proj
    . get_proj_var.sh "%s_SOURCEMAPS_DIR" $proj
    sentry-release.sh "$SENTRY_ORG" "$sentry_project" "$env" "$release" "$sourcemaps_url_prefix" "$sourcemaps_dir"
  fi

  # *** DEPLOY OR RUN ***
  if [ "$env" == "local" ]; then
    ./run.sh &
    pid="$!"
    run_sh_pids+="$pid " # for later cleanup

    sleep 5
    if ! ps -p $pid > /dev/null
    then
      echo "$0 [ERROR]: $proj/run.sh exited early, must be a crash."
      exit 1
    fi
  else
    # At least some projects rely on dotenv (flask, ?)
    # We generate a temporary .env dynamically from env-config/*.env then remove upon exit
    cp $top/env-config/$env.env $top/$proj/.env
    generated_envs+="$top/$proj/.env "

    # Get service variable name, <PROJECT>_APP_ENGINE_SERVICE
    . get_proj_var.sh "%s_APP_ENGINE_SERVICE" $proj
    sed -e 's/<SERVICE>/'$app_engine_service'/g' $top/$proj/app.yaml.template > $top/$proj/.app.yaml
    gcloud app deploy --quiet $top/$proj/.app.yaml
  fi
done

if [ "$env" == "local" ]; then
  sleep 1
  echo "Server process(es) are running. Press Ctrl+C to terminate..."
  while true; do sleep 86400; done
fi
