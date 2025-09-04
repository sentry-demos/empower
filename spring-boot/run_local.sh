#!/bin/bash

set -e

function cleanup {
  stop.sh java $SPRINGBOOT_LOCAL_PORT 
}
trap cleanup EXIT

./mvnw clean spring-boot:run -Dserver.port=$SPRINGBOOT_LOCAL_PORT 
