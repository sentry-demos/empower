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
#   SENTRY_ORG is passed to ./bin/sentry-release.sh and used to specify which Sentry
#   org to create release in.
#
#   <PROJECT>_SENTRY_PROJECT is passed to ./bin/sentry-release.sh and used to specify 
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
    projects+="$arg "
  fi
done

USAGE="[ERROR] Invalid arguments. Usage e.g.: ./deploy.sh --env=staging react flask"

# Validate CLI arguments
if [[ "$env" == "" || "$projects" == "" ]]; then
  echo "$USAGE"; 
  exit 1
fi

if [ "$env" == "production" ]; then
  if [ -t 0 ] ; then # shell is interactive
    verify_latest_code.sh
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

  echo "|||"
  echo "||| $0: $proj"
  echo "|||"

  validate_project.sh $top/$proj 
  
  cd $top/$proj

  # React bakes in (exported) env variables from calling shell as well as contents of .env
  # at build time into the static build output. As a result it doesn't need .env at runtime.
  # See: https://github.com/facebook/create-react-app/blob/main/packages/react-scripts/config/env.js
  # and https://create-react-app.dev/docs/adding-custom-environment-variables/
  #
  # Express and Flask on the other hand need .env deployed and present at runtime. 
  #
  # We generate a temporary .env dynamically from env-config/*.env then remove upon exit
  generated_envs+="$(../env.sh $env) "
  
  # We do this because 1) we need RELEASE that's generated in env.sh 2) we need *_APP_*_BACKEND
  # 3) some projects may require env variables instead of .env (not the case for react, flask & express)
  # TODO: support spring-boot which seems to use .properties files
  export $(grep -v '^#' .env | xargs) 
    
  if [[ "$env" == "local" && "$fe_projects" = *"$proj "* ]]; then 
    # Point to local backend http://host:port instead of cloud endpoints for all _built_ BE projects
    # If no backend projects specified in CLI args, keep using cloud (production or staging) BE endpoints.
    for be_proj in $be_projects; do
      backend_var=$(var_name.sh %s_APP_%s_BACKEND $proj $be_proj)
      . get_proj_var.sh "%s_APP_%s_BACKEND_LOCAL" $proj $be_proj # sets $app_backend_local
      echo "" >> .env # in case no newline
      echo "$backend_var=$app_backend_local" >> .env # append instead of search-replace should be OK
      export "$backend_var=$app_backend_local"
    done 
  fi

  unset CI # prevents build failing in GitHub Actions
  ./build.sh

  if [[ "$fe_projects" = *"$proj "* ]]; then # project is frontend
    sentry-release.sh $env $RELEASE
    # NOTE: Sentry may create releases from events even without this step
  fi

  # *** DEPLOY OR RUN ***
  if [ "$env" == "local" ]; then
    ./run.sh &
    pid="$!"
    run_sh_pids+="$pid " # for later cleanup

    if [[ "$projects" != *"$proj " ]]; then # not last one
      sleep 1 
      echo "$0: Waiting a few seconds before building next project to make sure this server process doesn't crash..."
      sleep 4 
      if ! ps -p $pid > /dev/null
      then
        echo "$0 [ERROR]: $proj/run.sh exited early, must be a crash."
        exit 1
      fi
    fi
  else

    # Replace <SERVICE> in app.yaml.template with <PROJECT>_APP_ENGINE_SERVICE
    . get_proj_var.sh "%s_APP_ENGINE_SERVICE" $proj
    sed -e 's/<SERVICE>/'$app_engine_service'/g' app.yaml.template > .app.yaml
    
    gcloud app deploy --quiet .app.yaml
  fi
done

if [ "$env" == "local" ]; then
  sleep 1
  echo "Server process(es) are running. Press Ctrl+C to terminate..."
  while true; do sleep 86400; done
fi
