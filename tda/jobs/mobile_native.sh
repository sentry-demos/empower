#!/bin/bash 

# Validation
if [[ "$LATEST_SENTRY_REACT_NATIVE_GITHUB_RELEASE" == "" || "$LATEST_ANDROID_GITHUB_RELEASE" == "" || \ 
      "$LATEST_IOS_GITHUB_RELEASE" == "" || "$LATEST_DOTNET_MAUI_GITHUB_RELEASE" == "" ]]; then
  echo '[ERROR] All of LATEST_SENTRY_REACT_NATIVE_GITHUB_RELEASE, LATEST_ANDROID_GITHUB_RELEASE, LATEST_IOS_GITHUB_RELEASE, and LATEST_DOTNET_MAUI_GITHUB_RELEASE must be set.'
  exit 1
fi

# Note: BATCH_SIZE currently not implemented in mobile tests
# Note: use '-s' instead of '-s -n 1' to be able to capture output:
#   "Due to how pytest-xdist is implemented, the -s/--capture=no option does not work."
#   https://pytest-xdist.readthedocs.io/en/stable/
pytest -s -n 3 mobile_native

