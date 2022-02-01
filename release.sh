# This if for Release Health. It sets a release according to Calendar Versioning and gets redeployed every day
# In sentry-demos/tracing we did not manage and autodeploy this daily, so you were stuck with the same Release for eternity until you redeployed
# /react and /flask both have a run.sh script that utilizes this code
day=$(date +%d)
month=$(date +%-m)
year=$(date +%y)
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