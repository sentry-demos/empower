#!/bin/bash

set -e

function cleanup {
  stop.sh java $SPRINGBOOT_LOCAL_PORT 
}
trap cleanup EXIT

# had to use application.properties because currently we don't export secrets, only substitute them in *.template files
./mvnw spring-boot:run -Dserver.port=$SPRINGBOOT_LOCAL_PORT #-Dspring.datasource.url=jdbc:postgresql://${DB_HOST}:5432/${DB_DATABASE}
