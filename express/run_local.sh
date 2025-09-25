#!/bin/bash

# This is not a standalone script. It is called from ../deploy that
# sets up the right environemnt variables and files for it.


function cleanup {
  stop.sh node $EXPRESS_LOCAL_PORT 
}
trap cleanup EXIT

npm install
PORT=$EXPRESS_LOCAL_PORT node server.js
