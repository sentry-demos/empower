#!/bin/bash

set -e

function cleanup {
  stop.sh dotnet $ASPNETCORE_LOCAL_PORT
}
trap cleanup EXIT

dotnet run -c Release --no-build --urls=http://localhost:$ASPNETCORE_LOCAL_PORT
