import requests
import os
from datetime import datetime

GITHUB_API_RELEASES_MAX_RESULTS = 30

GITHUB_REPOS = {
    'react_native': {
        'repo': 'sentry_react_native',
        'use_prefix': False
    },
    'android': {
        'repo': 'android', 
        'use_prefix': False
     },
    'ios': {
        'repo': 'ios',
        'use_prefix': True
    }
}

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
def latest_github_release(platform):
    release_version = os.getenv(f"LATEST_{platform.upper()}_GITHUB_RELEASE")
    if release_version is not None:
        # Fetch release version from environment variable.
        # This should be hit when bulk-generating TDA data
        return release_version
    else:
        # Fetch release version via Github API
        # This should be hit if the tests are being run locally
        print(f"Fetching {platform} release version from Github API...")
        return determine_latest_release_version(platform)

def latest_react_native_github_release():
    return latest_github_release('react_native')

def latest_android_github_release():
    return latest_github_release('android')

def latest_ios_github_release():
    return latest_github_release('ios')

def determine_latest_release_version(platform):
    repo = GITHUB_REPOS[platform]
    releases = requests.get(f"https://api.github.com/repos/sentry-demos/{repo['name']}/releases").json()
    if not repo['use_prefix']:
        # Assuming correct ordering (might cause bugs)
        return releases[0]['tag_name']
    else:
        # When using <platform>-1.2.3 format GH will order releases alphabetically, i.e. 0.0.21 -> 0.0.3
        # We can't use "Latest" because we have multiple latest releasese - one for each platform
        if len(releases) >= GITHUB_API_RELEASES_MAX_RESULTS:
            raise NotImplementedError(
                f"Github /releases API returned maximum number of results (${GITHUB_API_RELEASES_MAX_RESULTS}). " + 
                "Current implementation is not able to handle pagination. Please delete old releases or implement.") 

        platform_releases = list(filter(lambda r: r['tag_name'].startswith(platform + '-'), releases))
        # Parse the 'published_at' times and sort the releases
        platform_releases.sort(key=lambda release: datetime.strptime(release["published_at"], "%Y-%m-%dT%H:%M:%SZ"), reverse=True)
        return platform_releases[0]['tag_name']
