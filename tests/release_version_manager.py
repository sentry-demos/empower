import requests

def latest_react_native_github_release():
    react_native_releases = requests.get("https://api.github.com/repos/sentry-demos/sentry_react_native/releases")
    return react_native_releases.json()[0]['tag_name']