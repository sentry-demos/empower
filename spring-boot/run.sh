#!/bin/bash

set -e

function cleanup {
  stop.sh java $SPRINGBOOT_LOCAL_PORT 
}
trap cleanup EXIT

./mvnw spring-boot:run
