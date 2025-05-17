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
#
# Unfortunately a little clunky.
def latest_github_release(repo_name):
    release_version = os.getenv(f"LATEST_{repo_name.replace('-', '_').upper()}_GITHUB_RELEASE")
    if release_version is not None:
        # Fetch release version from environment variable.
        # This should be hit when bulk-generating TDA data
        return release_version
    else:
        # Fetch release version via Github API
        # This should be hit if the tests are being run locally
        print(f"Fetching {repo_name} release version from Github API...")
        return determine_latest_release_version(repo_name)

def latest_react_native_github_release():
    return latest_github_release('sentry_react_native')

def latest_android_github_release():
    return latest_github_release('android')

def latest_ios_github_release():
    return latest_github_release('ios')

def latest_dotnet_maui_github_release():
    return latest_github_release('dotnet-maui')

def determine_latest_release_version(repo_name):
    releases = requests.get(f"https://api.github.com/repos/sentry-demos/{repo_name}/releases")
    return releases.json()[0]['tag_name']
