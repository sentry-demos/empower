#!/bin/bash

function cleanup {
  stop.sh php $LOCAL_PORT 
}
trap cleanup EXIT

php artisan serve --port=$LOCAL_PORT

