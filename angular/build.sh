#!/bin/bash

set -e  # Exit immediately if any command fails

echo "Cleaning previous build..."
rm -rf dist

# Always install dependencies to ensure Angular CLI is available
echo "📥 Installing dependencies..."
npm install

# This creates optimized production bundles with minification and tree-shaking
echo "🔨 Building Angular application..."
npm run build:ng

if [ -z "${ANGULAR_SENTRY_ENVIRONMENT}" -o -z "${SENTRY_ORG}" -o -z "${ANGULAR_SENTRY_PROJECT}" -o -z "${ANGULAR_RELEASE}" ]; then
    echo "❌ One of the required env variables not set: ANGULAR_SENTRY_ENVIRONMENT, SENTRY_ORG, ANGULAR_SENTRY_PROJECT, ANGULAR_RELEASE"
    exit 1
fi   

# Process source maps for Sentry using the shared script
echo "Uploading Sentry source maps..."
sentry-release.sh ${ANGULAR_SENTRY_ENVIRONMENT} ${SENTRY_ORG} ${ANGULAR_SENTRY_PROJECT} ${ANGULAR_RELEASE}

# Verify build output
# Check that the build completed successfully and show build information
if [ -d "dist" ]; then
    echo "✅ Build completed successfully!"
else
    echo "❌ Build failed! dist/ directory not found."
    exit 1
fi
