import requests
import os

# Setting the release version in an environment variable
# upfront (via higher level scripts script.sh or mobile_native.sh)
# and then fetching it here prevents us from exceeding Github's API rate limits
# when generating bulk automated data (1 api call upfront instead
# of 1 for every individual test run).
#
# However, we still benefit from the ability to run these tests directly,
# not only from one of the infinite-loop shell scripts used to generate data in bulk.
# This function allows for that as well.
#
# Unfortunately a little clunky.
#
def latest_react_native_github_release():
    release_version = os.getenv("LATEST_REACT_NATIVE_GITHUB_RELEASE")
    if release_version is not None:
        # This should happen if we're bulk-generating TDA data
        print("Fetching React Native release version from env variable")
        return release_version
    else:
        # This should happen if the tests are being run locally
        print("Fetching React Native release version from Github API...")
        return fetch_latest_react_native_release_version()

def fetch_latest_react_native_release_version():
    react_native_releases = requests.get("https://api.github.com/repos/sentry-demos/sentry_react_native/releases")
    return react_native_releases.json()[0]['tag_name']
