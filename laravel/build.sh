#!/bin/bash

set -e

php artisan optimize:clear
php artisan optimize

php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan event:cache