#!/bin/bash
# Compile excimer.so for Linux x86_64 (matching GAE standard PHP 8.3 runtime)
# Run this locally whenever you need to update the bundled excimer.so

set -e

docker run --rm --platform linux/amd64 \
  -v "$(pwd):/out" \
  php:8.3-cli \
  bash -c '
    pecl install excimer && \
    cp "$(php -r "echo ini_get(\"extension_dir\");")/excimer.so" /out/excimer.so
  '

echo "Built excimer.so:"
file excimer.so
