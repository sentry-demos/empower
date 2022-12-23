#!/bin/bash

LOCAL_PORT=8000

function cleanup {
  # This is copied form application-monitoring/bin/stop.sh
  # TODO replace with `stop.sh php $LOCAL_PORT` once moved into that repository
  server_pid=""
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    server_pid="$(netstat -lnp | grep $LOCAL_PORT | head -1 | awk '{ print $7 }' | cut -d '/' -f 1)"
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    server_pid="$(netstat -anv | grep $LOCAL_PORT | grep LISTEN | cut -w -f 9)"
  fi
  if [ "$server_pid" != "" ]; then
    kill "$server_pid" 2>/dev/null
  fi
}
trap cleanup EXIT

php artisan serve --port=$LOCAL_PORT

