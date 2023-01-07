#!/bin/bash

set -e

properties="./src/main/resources/application.properties"

echo "spring.datasource.url=jdbc:postgresql://$DB_HOST:5432/$DB_DATABASE" >> $properties
echo "server.port=$LOCAL_PORT" >> $properties
echo "spring.cloud.gcp.sql.enabled=false" >> $properties

function cleanup {
  stop.sh java $LOCAL_PORT 
}
trap cleanup EXIT

./mvnw spring-boot:run
