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

SENTRY_ORG=testorg-az
SENTRY_PROJECT=javascript-react
PREFIX=static/js
REPOSITORY=us.gcr.io/sales-engineering-sf

sentry-cli releases -o $SENTRY_ORG new -p $SENTRY_PROJECT $RELEASE
sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT set-commits --auto $RELEASE
sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT files $RELEASE upload-sourcemaps --url-prefix "~/static/js" --validate react/build/$PREFIX

# RELEASE was already baked into the prod build, so no need to `--update-env-vars` it for the React app
npm run build && gcloud app deploy
echo 'REACT DEPLOY DONE'


# `gcloud app deploy` does not support `--update-env-vars RELEASE=$RELEASE`
# cd flask && gcloud app deploy 
echo 'FLASK DEPLOY DONE'
