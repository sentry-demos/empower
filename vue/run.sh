#!/bin/sh

./build_and_upload_sourcemaps.sh --clean-first
npx serve -s dist
