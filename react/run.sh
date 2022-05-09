# Builds and serves the js bundle, uploads sourcemaps and does suspect commits

PACKAGE=application.monitoring.javascript
VERSION=`../release.sh`
RELEASE=$PACKAGE@$VERSION
echo $RELEASE

SENTRY_ORG=testorg-az
SENTRY_PROJECT=application-monitoring-javascript
PREFIX=static/js

npm run build

sentry-cli releases -o $SENTRY_ORG new -p $SENTRY_PROJECT $RELEASE
sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT set-commits --auto $RELEASE
sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT files $RELEASE upload-sourcemaps --url-prefix "~/static/js" --validate build/$PREFIX

serve -s build