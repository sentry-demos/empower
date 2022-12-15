#!/bin/bash

set -e

properties="./src/main/resources/application.properties"

echo "spring.datasource.url=jdbc:postgresql://$HOST:5432/$DATABASE" >> $properties
echo "server.port=$LOCAL_PORT" >> $properties
echo "spring.cloud.gcp.sql.enabled=false" >> $properties

function cleanup {
  stop.sh java $LOCAL_PORT 
}
trap cleanup EXIT

./mvnw spring-boot:run
