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

time_segment() {
  hour="$1"
  segment=$(( (hour / 6) * 2 + (hour % 6 < 5 ? 0 : 1) ))
  echo "$segment"
}

is_next_hour_in_new_segment() {
  hour="$1"
  current_segment=$(time_segment "$hour")
  next_hour=$((hour + 1))
  if [[ "$next_hour" -gt 23 ]]; then
    echo 1
    return
  fi
  next_segment=$(time_segment "$next_hour")
  if [[ "$current_segment" -ne "$next_segment" ]]; then
    echo 1
  else
    echo 0
  fi
}

# Note that we use UTC time (-u)
month=$(date -u "${delta[@]}" +%-m)
year=$(date -u "${delta[@]}" +%y)
hour=$(date -u "${delta[@]}" +%H)

# the idea is that we will create a new release at the end of the last hour of a segment
# ideally around 55 - 59 minutes into the hour (since deployment might take 5 minutes)
# TODO: if our cron scheduling can run late we may need to either A) adjust time / round dow to previous hour
# or B) get release version at the very start of deploy.sh so that if deployment takes long we don't switch
# to next hour.
result=$(is_next_hour_in_new_segment "$hour")
if [ "$result" -eq 0 ]; then
  # keep going back 1 hour until we find a new segment or hit 0
  while [ "$result" -eq 0 ] && [ "$hour" -gt 0 ]; do
    hour=$((hour - 1))
    result=$(is_next_hour_in_new_segment "$hour")
  done
  # if hour is not 0 go 1 hour forward
  if [ "$hour" -ne 0 ]; then
    hour=$((hour + 1))
  fi
fi

month_hour=$(( ($(date -u +%d) - 1) * 24 + $hour )) # from 0 to 743

echo "$year.$month.$month_hour"
