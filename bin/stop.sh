#!/bin/bash

#
# Stop background server process with given name listening on given port
#

USAGE="Usage: ./stop.sh node 3000"

server_cmd="$1"
server_port="$2"

if [[ $server_cmd == "" || server_port == "" ]]; then
    echo "[error] Missing required command-line arguments."
    echo "$USAGE"
fi

server_pid=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    server_pid="$(netstat -lnp | grep $server_port | head -1 | awk '{ print $7 }' | cut -d '/' -f 1)"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    server_pid="$(netstat -anv | grep $server_port | grep LISTEN | head -1 | cut -w -f 9)"
fi

if [ "$server_pid" != "" ]; then 
    kill "$server_pid" 2>/dev/null
else
    :
    #echo "$0: unable to identify process listening on port $server_port. Using 'killall $server_cmd' instead."
    #killall $server_cmd
fi
