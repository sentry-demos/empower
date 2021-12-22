# fetch and set release version upfront to reduce unnecessary API calls and avoid Github API rate limiting
export LATEST_REACT_NATIVE_GITHUB_RELEASE=$(python3 latest_github_release.py react_native)
export LATEST_ANDROID_GITHUB_RELEASE=$(python3 latest_github_release.py android)

echo "React Native v$(LATEST_REACT_NATIVE_GITHUB_RELEASE)"
echo "Android v$(LATEST_ANDROID_GITHUB_RELEASE)"

while true; do clear && pytest -s -n 4 .; done
