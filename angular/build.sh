#!/bin/bash

# Angular Production Build Script
# This script builds the Angular application for production deployment
# It handles environment variable substitution and creates optimized bundles
#
# What this script does:
# 1. Sets up environment variables for the build
# 2. Cleans previous build artifacts
# 3. Installs dependencies if needed
# 4. Builds the Angular application with production optimizations
# 5. Processes source maps for Sentry error monitoring
# 6. Verifies the build output
#
# Usage:
#   ./build.sh                    # Build with default environment
#   RELEASE=v1.2.3 ./build.sh    # Build with specific release version
#   ENVIRONMENT=staging ./build.sh # Build for specific environment

set -e  # Exit immediately if any command fails

echo "🏗️ Building Angular application for production..."

# Check if we're in the right directory
# This prevents accidentally running the script from the wrong location
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the angular directory."
    exit 1
fi

# Check if required environment variables are set
# These variables control the build configuration and Sentry integration
if [ -z "$RELEASE" ]; then
    echo "⚠️  Warning: RELEASE environment variable not set. Using 'dev' as default."
    export RELEASE="dev"
fi

if [ -z "$ENVIRONMENT" ]; then
    echo "⚠️  Warning: ENVIRONMENT variable not set. Using 'local' as default."
    export ENVIRONMENT="local"
fi

echo "📦 Release: $RELEASE"
echo "🌍 Environment: $ENVIRONMENT"

# Clean previous build
# Remove old build artifacts to ensure a clean build
echo "🧹 Cleaning previous build..."
rm -rf dist

# Install dependencies if needed
# Always install dependencies to ensure Angular CLI is available
echo "📥 Installing dependencies..."
npm install

# Set default backend URLs for local development if not specified
if [ "$ENVIRONMENT" == "local" ]; then
  if [ -z "$ANGULAR_APP_FLASK_BACKEND" ]; then
    export ANGULAR_APP_FLASK_BACKEND="http://localhost:8080"
  fi
  if [ -z "$ANGULAR_APP_LARAVEL_BACKEND" ]; then
    export ANGULAR_APP_LARAVEL_BACKEND="http://localhost:8000"
  fi
fi

# Build the application
# This creates optimized production bundles with minification and tree-shaking
echo "🔨 Building Angular application..."
npm run build:ng

# Process source maps for Sentry using the shared script
echo "📤 Processing source maps for Sentry..."
if [ -f "../bin/sentry-release.sh" ]; then
    ../bin/sentry-release.sh $ENVIRONMENT $RELEASE true
else
    echo "⚠️  Warning: ../bin/sentry-release.sh not found. Skipping Sentry source map upload."
fi

# Verify build output
# Check that the build completed successfully and show build information
if [ -d "dist" ]; then
    echo "✅ Build completed successfully!"
    echo "📁 Build output: dist/"
    echo "📊 Bundle size:"
    du -sh dist/*
else
    echo "❌ Build failed! dist/ directory not found."
    exit 1
fi

echo "🚀 Angular application is ready for deployment!"
