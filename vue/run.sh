#!/bin/sh

# This is not a standalone script. It is called from ../deploy.sh that
# sets up the right environemnt variables and files for it.

./build_and_upload_sourcemaps.sh --clean-first
npx serve -s dist
