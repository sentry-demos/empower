#!/bin/bash

set -e

properties="./src/main/resources/application.properties"

echo "spring.datasource.url=jdbc:postgresql://$HOST:5432/$DATABASE" >> $properties
echo "server.port=8090" >> $properties
echo "spring.cloud.gcp.sql.enabled=false" >> $properties


./mvnw spring-boot:run