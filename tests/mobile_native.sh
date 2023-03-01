# fetch and set release version upfront to reduce unnecessary API calls and avoid Github API rate limiting
export LATEST_REACT_NATIVE_GITHUB_RELEASE=$(python3 latest_github_release.py react_native)
export LATEST_ANDROID_GITHUB_RELEASE=$(python3 latest_github_release.py android)

echo "React Native Github Release v$LATEST_REACT_NATIVE_GITHUB_RELEASE"
echo "Android Github Release v$LATEST_ANDROID_GITHUB_RELEASE"

# Note: BATCH_SIZE currently not used in mobile tests
while true; do clear && SE_TAG=tda BATCH_SIZE=random_20 pytest -s -n 4 mobile_native; done
