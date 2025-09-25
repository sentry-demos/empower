// Environment configuration for Angular
// Uses webpack DefinePlugin to inject environment variables at build time
// This single file handles all environments (development, staging, production)

export const environment = {
  production: ['production', 'staging'].includes(process.env['SENTRY_ENVIRONMENT'] || ''),
  
  DSN: process.env['DSN'],
  RELEASE: process.env['RELEASE'],
  SENTRY_ENVIRONMENT: process.env['SENTRY_ENVIRONMENT'],
  BACKEND_URL_FLASK: process.env['BACKEND_URL_FLASK'],
  BACKEND_URL_LARAVEL: process.env['BACKEND_URL_LARAVEL'],
};
