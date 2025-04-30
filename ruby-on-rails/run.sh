#!/bin/bash

set -e

bundle install
bundle exec rackup -s Puma -p $RUBYONRAILS_LOCAL_PORT
