import release_version_manager
import sys

# This printed release version is captured via a higher-level shell script, i.e. script.sh
# or mobile_native.sh, and stored as an environment variable.
if len(sys.argv) != 2:
	raise ValueError("This script expects you to pass a command line argument for the desired platform, i.e. `python3 <this_script.py> react_native`.")

platform = sys.argv[1]
release_ver = release_version_manager.determine_latest_release_version(platform)

# Don't delete this print statement, it's captured in an environment
# variable as output.
print(release_ver)
