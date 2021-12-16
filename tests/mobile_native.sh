# fetch and set release version upfront to reduce unnecessary API calls and avoid Github API rate limiting
export LATEST_REACT_NATIVE_GITHUB_RELEASE=$(python3 latest_react_native_github_release.py)

while true; do clear && pytest -s -n 4 mobile_native; done
