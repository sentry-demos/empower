#!/bin/bash

path="$1"
proj=$(basename $path)

set -e 
  
if [ ! -d $path ]; then
    echo "[ERROR] Project '$proj' does not exist"
    exit 1
fi

if [ "$proj" != "spring-boot" ]; then
    if [ -f "$path/app.yaml" ]; then 
        echo "[ERROR] project '$proj' contains legacy app.yaml file that is no longer used. Please delete this file,
        it is no longer be needed and has been replaced by app.yaml.template."
        exit 1
    elif [ ! -f "$path/app.yaml.template" -a ! -f "$path/deploy_project.sh" ]; then
        echo "[ERROR] Project $proj must contain either app.yaml.template with '<SERVICE>' placeholder OR a deploy_project.sh script."
        exit 1
    fi
fi
