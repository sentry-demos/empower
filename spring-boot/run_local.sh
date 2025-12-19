#!/bin/bash

set -e

function cleanup {
  stop.sh java $SPRINGBOOT_LOCAL_PORT 
}
trap cleanup EXIT

./mvnw clean spring-boot:run -Dspring-boot.run.arguments=--server.port=$SPRINGBOOT_LOCAL_PORT 
