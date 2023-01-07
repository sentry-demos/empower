#!/bin/bash

set -e

properties="./src/main/resources/application.properties"

cp ./src/main/resources/application.properties.template $properties

echo "" >> $properties # newline
echo "sentry.dsn=$SPRINGBOOT_APP_DSN" >> $properties
echo "spring.datasource.username=$DB_USERNAME" >> $properties
echo "spring.datasource.password=$DB_PASSWORD" >> $properties
echo "spring.cloud.gcp.sql.database-name=$DB_DATABASE" >> $properties
#This value is formatted in the form: [gcp-project-id]:[region]:[instance-name]
echo "spring.cloud.gcp.sql.instance-connection-name=$DB_CLOUD_SQL_CONNECTION_NAME" >> $properties

#GCP
# NOTE: if run.sh is called after build.sh it must overwrite this value
echo "spring.cloud.gcp.sql.enabled=true" >> $properties
