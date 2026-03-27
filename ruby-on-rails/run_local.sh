#!/bin/bash

set -e

function cleanup {
    stop.sh puma $RUBYONRAILS_LOCAL_PORT
}
trap cleanup EXIT

bundle install
bundle exec rackup -s Puma -p $RUBYONRAILS_LOCAL_PORT
