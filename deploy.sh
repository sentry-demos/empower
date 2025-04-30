#!/bin/bash

# deploy.sh - build, upload artifacts, and deploy or run locally any one or multiple projects
# using ./env-config/*.env for both build-time and runtime environment configuration, where --env 
# parameter specifies which env-config file to use. A special case is --env=local which will run 
# each project's 'run.sh' script instead of deploying to Google App Engine. If multiple projects
# are specified on command-line in this local mode, a webserver will be started for each project.
#
# Usage: ./deploy.sh react flask --env=staging
#
# All variables in *.env are passed into each projects runtime environment.
# Some variables, however, are special and are additionally used during the build:
#
#   SENTRY_ORG and <PROJECT>_SENTRY_PROJECT are used in ./bin/sentry-release.sh (or build plugin 
#   config templates, e.g. webpack.config.js) to upload releases and/or sourcemaps.
#
#   REACT_APP_<PROJECT>_BACKEND besides being passed into React application runtime these are
#   substituted with the values of respective REACT_APP_<PROJECT>_BACKEND_LOCAL when --env=local
#   AND <PROJECT> is included in the list of projects to build from command-line arguments.

set -e

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
  if [[ $proj =~ ^(flask|express|ruby|spring-boot|aspnetcore|laravel|ruby-on-rails|crons-python)$ ]]; then
    be_projects+="$proj "
  else
    fe_projects+="$proj "
  fi
done
projects="$be_projects $fe_projects"

function cleanup {
  for pid in $run_sh_pids; do
    # each run.sh has it's own cleanup function
    if ps -p $pid > /dev/null; then
      kill $pid 2>/dev/null
    fi
  done
  if [ "$temp_files" != "" ]; then
    rm -f $temp_files # bash only (passed as separate args)
  fi
}
trap cleanup EXIT

run_sh_pids=""
temp_files=""

function wait_check_if_crashed {
  local pid=$1
  local proj=$2
  sleep 1
  echo "$0: Waiting a few seconds before building next project to make sure this server process doesn't crash..."
  sleep 4
  if ! ps -p $pid > /dev/null
  then
    echo "$0 [ERROR]: $proj/run.sh exited early, must be a crash."
    exit 1
  fi
}

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
  temp_files+="$(../env.sh $env) "

  # We do this because 1) we need RELEASE that's generated in env.sh 2) we need *_APP_*_BACKEND
  # 3) some projects may require env variables instead of .env (not the case for react, flask & express)
  # TODO: double check above comment is still correct, we do this 3 times (once here and twice in env.sh)
  # TODO: support spring-boot which seems to use .properties files
  export $(grep -v '^#' .env | sed 's/ #.*//' | xargs)

  if [[ "$env" == "local" && "$fe_projects" = *"$proj "* ]]; then
    # Point to local backend http://host:port instead of cloud endpoints for all _built_ BE projects
    # If no backend projects specified in CLI args, keep using cloud (production or staging) BE endpoints.
    for be_proj in $be_projects; do
      if  [ "$proj" == "next" ]; then
        # Next env variables need to start with NEXT_PUBLIC_*
        backend_var=$(var_name.sh NEXT_PUBLIC_%s_BACKEND $be_proj)
      else
        backend_var=$(var_name.sh %s_APP_%s_BACKEND $proj $be_proj)
      fi
      . get_proj_var.sh "%s_LOCAL_PORT" $be_proj # sets $local_port
      echo "" >> .env # in case no newline
      backend_local="http://localhost:$local_port"
      echo "$backend_var=$backend_local" >> .env # append instead of search-replace should be OK
      export "$backend_var=$backend_local"
    done
  fi

  unset CI # prevents build failing in GitHub Actions
  ./build.sh

  if [[ $proj =~ ^(react|next|vue|flask)$ ]]; then # Suspect Commits now require commits associated w/ release
    if [[ $proj == "vue" ]]; then
      upload_sourcemaps="true"
    else
      upload_sourcemaps="false" # using webpack plugin or doesn not apply
    fi
    sentry-release.sh $env $RELEASE $upload_sourcemaps
    # NOTE: Sentry may create releases from events even without this step
  fi

  # If gcloud is installed, use it to get the sentry auth token from Google Cloud Secret Manager.
  # Sentry CLI will use this token for authentication.  Otherwise, one can use `sentry-cli login`,
  # but that will not work when deploying to staging or production.
  if command -v gcloud &> /dev/null ; then
    export SENTRY_AUTH_TOKEN=$(gcloud secrets versions access latest --secret="SENTRY_AUTH_TOKEN")
  fi

  # TODO: rename to *.empower-template if ever conflicts with some language's template files
  templates=$(find . -type f -name "*.template")
  for template in $templates; do
    envsubst.sh < $template > ${template%.template}
    temp_files+="${template%.template} "
  done
  
  # *** DEPLOY OR RUN ***
  if [ "$env" == "local" ]; then
    ./run.sh &
    pid="$!"
    run_sh_pids+="$pid " # for later cleanup

    if [[ "$projects" != *"$proj " ]]; then # not last one
      wait_check_if_crashed "$pid" "$proj"
    fi
  else
    if [ -f deploy_project.sh ]; then
      ./deploy_project.sh
    elif [ "$proj" == "spring-boot" ]; then
      mvn clean package appengine:deploy
    else
      gcloud app deploy --version v1 --quiet .app.yaml
    fi

  fi
done

if [ "$env" == "local" ]; then
  sleep 1
  echo "Server process(es) are running. Press Ctrl+C to terminate..."
  while true; do sleep 86400; done
fi
