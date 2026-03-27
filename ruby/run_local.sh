#!/bin/bash

set -e

source gcloud-ignore-workaround.env

function cleanup {
    rm -f tmp
    stop.sh ruby $RUBY_LOCAL_PORT
}
trap cleanup EXIT

bundle install
mkdir -p tmp/pids
PORT=$RUBY_LOCAL_PORT ruby main.rb