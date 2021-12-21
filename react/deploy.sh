RELEASE=`../release.sh`
echo $RELEASE

SENTRY_ORG=testorg-az
SENTRY_PROJECT=application-monitoring-javascript
PREFIX=static/js

rm -rf build
npm install
npm run build

sentry-cli releases -o $SENTRY_ORG new -p $SENTRY_PROJECT $RELEASE
sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT set-commits --auto $RELEASE
sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT files $RELEASE upload-sourcemaps --url-prefix "~/static/js" --validate build/$PREFIX

# This deploys React - The release was set in the static prod build
gcloud app deploy --quiet