#!/bin/bash

function cleanup {
  stop.sh php $LOCAL_PORT 
}
trap cleanup EXIT

composer install
php artisan serve --port=$LOCAL_PORT

