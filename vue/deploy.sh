# Builds and serves the js bundle, uploads sourcemaps and does suspect commits

# RELEASE=`../release.sh`

PACKAGE="application.monitoring.vue"
VERSION=`./release.sh`
RELEASE=$PACKAGE@$VERSION

echo $RELEASE

SENTRY_ORG=testorg-az
SENTRY_PROJECT=will-vue-f2
PREFIX=assets

npm run build

sentry-cli releases -o $SENTRY_ORG new -p $SENTRY_PROJECT $RELEASE
sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT set-commits --auto $RELEASE
sentry-cli releases -o $SENTRY_ORG -p $SENTRY_PROJECT files $RELEASE upload-sourcemaps --url-prefix "~/assets" --validate dist/$PREFIX

# This deploys React - The release was set in the static prod build
gcloud app deploy --quiet