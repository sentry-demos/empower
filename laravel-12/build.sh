#!/bin/bash

set -e 

echo "" >> .env
echo "APP_NAME=Laravel" >> .env
echo "APP_ENV=local" >> .env
echo "APP_KEY=$(php artisan key:generate --show)" >> .env
echo "APP_DEBUG=true" >> .env
echo "APP_URL=http://localhost" >> .env

echo "LOG_CHANNEL=stack" >> .env
echo "DB_HOST=$DB_HOST" >> .env

composer install --optimize-autoloader --no-dev
php artisan config:cache
php artisan route:cache 