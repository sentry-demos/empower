#!/bin/bash

set -e 

echo "" >> .env
echo "APP_NAME=Laravel" >> .env
echo "APP_ENV=local" >> .env
echo "APP_KEY=base64:Gb/dwJD0MnQst35coE7tJMqCOcVXTkJbBCOmwXNdkJk=" >> .env
echo "APP_DEBUG=true" >> .env
echo "APP_URL=http://localhost" >> .env

echo "LOG_CHANNEL=stack" >> .env
echo "DB_HOST=$DB_HOST" >> .env
