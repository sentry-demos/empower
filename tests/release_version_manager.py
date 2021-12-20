import requests
import os

GITHUB_REPOS = {
    # platform: <github repo name>
    'react_native': 'sentry_react_native',
    'android': 'android'
}

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

# 'platform' parameter is 'android', 'react_native', etc...
def latest_github_release(platform):
    release_version = os.getenv(f"LATEST_{platform.upper()}_GITHUB_RELEASE")
    if release_version is not None:
        # This should happen if we're bulk-generating TDA data
        print(f"Fetching {platform} release version from env variable")
        return release_version
    else:
        # This should happen if the tests are being run locally
        print(f"Fetching {platform} release version from Github API...")
        repo_name = GITHUB_REPOS[platform]
        return fetch_latest_release_version(repo_name)

def latest_react_native_github_release():
    return latest_github_release('react_native')

def latest_android_github_release():
    return latest_github_release('android')

def fetch_latest_release_version(repo_name):
    react_native_releases = requests.get(f"https://api.github.com/repos/sentry-demos/{repo_name}/releases")
    return react_native_releases.json()[0]['tag_name']
