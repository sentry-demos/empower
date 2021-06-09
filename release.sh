# Sets a release according to Calendar Versioning. Month, followed by week of the month.
# In sentry-demos/tracing, we did not manage this whatsoever
# This release.sh is re-used in many places so that we don't need 3 different Makefiles like in sentry-demos/tracing
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