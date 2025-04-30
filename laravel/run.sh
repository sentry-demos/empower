#!/bin/bash

function cleanup {
  stop.sh php $LARAVEL_LOCAL_PORT 
}
trap cleanup EXIT

php artisan serve --port=$LARAVEL_LOCAL_PORT

