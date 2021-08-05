# Sets a release according to Calendar Versioning. Month, followed by week of the month.
# In sentry-demos/tracing, we did not manage this whatsoever
# /react and /flask both have a run.sh script that utilizes this code
# This release.sh is used by deploy.sh, react/run.sh, flask/run.sh
day=$(date +%d)
month=$(date +%-m)
if [ "$day" -ge 0 ] && [ "$day" -le 7 ]; then
  week=1
elif [ "$day" -ge 8 ] &&  [ "$day" -le 14 ]; then
  week=2
elif [ "$day" -ge 15 ] &&  [ "$day" -le 21 ]; then
  week=3
elif [ "$day" -ge 22 ]; then
  week=4
fi
echo "$month.$week"