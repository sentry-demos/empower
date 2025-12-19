#!/bin/bash

set -e  # Exit immediately if any command fails

echo "Cleaning previous build..."
rm -rf dist

# Always install dependencies to ensure Angular CLI is available
echo "📥 Installing dependencies..."
npm install

# Validate required Sentry environment variables before build
if [ -z "${ANGULAR_SENTRY_ENVIRONMENT}" -o -z "${SENTRY_ORG}" -o -z "${ANGULAR_SENTRY_PROJECT}" -o -z "${ANGULAR_RELEASE}" ]; then
    echo "❌ One of the required env variables not set: ANGULAR_SENTRY_ENVIRONMENT, SENTRY_ORG, ANGULAR_SENTRY_PROJECT, ANGULAR_RELEASE"
    exit 1
fi

# Validate SENTRY_AUTH_TOKEN is available for source map upload
if [ -z "${SENTRY_AUTH_TOKEN}" ]; then
    echo "❌ SENTRY_AUTH_TOKEN is not set. Required for source map upload."
    exit 1
fi

# This creates optimized production bundles with minification and tree-shaking
# The @sentry/webpack-plugin will automatically upload source maps during the build
echo "🔨 Building Angular application (with automatic source map upload)..."
npm run build:ng

# Associate git commits with the release for suspect commits feature
# This enables Sentry to show which commits likely caused an error
echo "📝 Linking git commits to release..."
sentry-release.sh ${ANGULAR_SENTRY_ENVIRONMENT} ${SENTRY_ORG} ${ANGULAR_SENTRY_PROJECT} ${ANGULAR_RELEASE}

# Verify build output
if [ -d "dist" ]; then
    echo "✅ Build completed successfully!"
    echo "✅ Source maps uploaded and commits linked (release: ${ANGULAR_RELEASE})"
else
    echo "❌ Build failed! dist/ directory not found."
    exit 1
fi
