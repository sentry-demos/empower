const webpack = require('webpack');
const path = require('path');

module.exports = {
  // This webpack config will be used by Angular CLI via @angular-builders/custom-webpack
  plugins: [
    new webpack.DefinePlugin({
      // Define environment variables that will be available in the Angular app
      'process.env': {
        'ANGULAR_APP_ENVIRONMENT': JSON.stringify(process.env.ANGULAR_APP_ENVIRONMENT || 'local'),
        'ANGULAR_APP_RELEASE': JSON.stringify(process.env.ANGULAR_APP_RELEASE || 'dev'),
        'ANGULAR_APP_DSN': JSON.stringify(process.env.ANGULAR_APP_DSN || ''),
        'ANGULAR_APP_FLASK_BACKEND': JSON.stringify(process.env.ANGULAR_APP_FLASK_BACKEND || 'http://localhost:8080'),
        'ANGULAR_APP_LARAVEL_BACKEND': JSON.stringify(process.env.ANGULAR_APP_LARAVEL_BACKEND || 'http://localhost:8000'),
        'ANGULAR_SENTRY_PROJECT': JSON.stringify(process.env.ANGULAR_SENTRY_PROJECT || 'angular'),
        'ANGULAR_SOURCEMAPS_DIR': JSON.stringify(process.env.ANGULAR_SOURCEMAPS_DIR || 'dist/empower-angular'),
        'ANGULAR_SOURCEMAPS_URL_PREFIX': JSON.stringify(process.env.ANGULAR_SOURCEMAPS_URL_PREFIX || '~/'),
        'ANGULAR_RELEASE_PACKAGE_NAME': JSON.stringify(process.env.ANGULAR_RELEASE_PACKAGE_NAME || 'application.monitoring.angular')
      }
    })
  ]
};
