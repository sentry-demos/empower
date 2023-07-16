#!/bin/bash

# This if for Release Health. It sets a release according to Calendar Versioning and gets redeployed every day
# In sentry-demos/tracing we did not manage and autodeploy this daily, so you were stuck with the same Release for eternity until you redeployed
# /react and /flask both have a run.sh script that utilizes this code

# Example: 
# ./release.sh
# Calendar release version for today
# ./release.sh 2 
# Calendar release version for 2 days ago 

# Check any command line arguments passed
if [ $# -gt 0 ]; then
  if [[ $(uname) == "Darwin" ]]; then
    delta=("-v-${1}d")
  else
    delta=(
      "-d"
      "$1 days ago"
    )
  fi
fi

# Note that we use UTC time (-u)
day=$(date -u "${delta[@]}" +%d)
month=$(date -u "${delta[@]}" +%-m)
year=$(date -u "${delta[@]}" +%y)

if [ "$day" -ge 0 ] && [ "$day" -le 7 ]; then
  week=1
elif [ "$day" -ge 8 ] &&  [ "$day" -le 14 ]; then
  week=2
elif [ "$day" -ge 15 ] &&  [ "$day" -le 21 ]; then
  week=3
elif [ "$day" -ge 22 ] && [ "$day" -le 28 ]; then
  week=4
elif [ "$day" -ge 29 ] && [ "$day" -le 35 ]; then
  week=5
fi
echo "$year.$month.$week"
