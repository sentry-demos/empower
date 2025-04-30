#!/bin/sh

# This is not a standalone script. It is called from ../deploy.sh that
# sets up the right environemnt variables and files for it.

source .env

./build.sh
npx serve -s dist
