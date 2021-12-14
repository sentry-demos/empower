import release_version_manager

# This printed release version is captured via a higher-level shell script, i.e. script.sh
# or mobile_native.sh, and stored as an environment variable.

release_ver = release_version_manager.fetch_latest_react_native_release_version()
print(release_ver)
