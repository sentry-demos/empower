#!/bin/bash

set -e

bundle install
bundle exec rackup -s Puma -p $LOCAL_PORT
