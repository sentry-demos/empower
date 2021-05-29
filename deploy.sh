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
RELEASE="$month.$week"
echo $RELEASE

# TODO - test all this, and remove Release code above

# RELEASE was already baked into the prod build, so no need to `--update-env-vars` it for the React app
gcloud app deploy

# `gcloud app deploy` does not support `--update-env-vars RELEASE=$RELEASE`
cd flask && gcloud app deploy 