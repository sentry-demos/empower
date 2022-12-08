#!/bin/bash

set -e

function cleanup {
  stop.sh dotnet $ASPNETCORE_LOCAL_PORT
}
trap cleanup EXIT

dotnet run --urls=http://localhost:$ASPNETCORE_LOCAL_PORT


