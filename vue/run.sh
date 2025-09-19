#!/bin/sh

# This is not a standalone script. It is called from ../deploy.sh that
# sets up the right environemnt variables and files for it.

npx serve -s dist -c ../serve.json