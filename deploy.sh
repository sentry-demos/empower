RELEASE=`./release.sh`
echo $RELEASE

SENTRY_ORG=will-captel
SENTRY_PROJECT=application-monitoring-javascript
PREFIX=static/js
REPOSITORY=us.gcr.io/sales-engineering-sf

npm run build

sentry-cli releases -o $SENTRY_ORG new -p $SENTRY_PROJECT $RELEASE
# sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT set-commits --auto $RELEASE
sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT files $RELEASE upload-sourcemaps --url-prefix "~/static/js" --validate build/$PREFIX

# The release was set in the static prod build
gcloud app deploy

# # `gcloud app deploy` does not support `--update-env-vars RELEASE=$RELEASE`
# cd flask && gcloud app deploy 
# echo 'FLASK DEPLOY DONE'
