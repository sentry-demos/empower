// Environment configuration for Angular
// Uses webpack DefinePlugin to inject environment variables at build time
// This single file handles all environments (development, staging, production)

export const environment = {
  production: ['production', 'staging'].includes(process.env['SENTRY_ENVIRONMENT'] || ''),
  
  DSN: process.env['DSN'],
  RELEASE: process.env['RELEASE'],
  SENTRY_ENVIRONMENT: process.env['SENTRY_ENVIRONMENT'],
  
  // Backend URLs - supports 6 backends like React
  BACKEND_URL_FLASK: process.env['BACKEND_URL_FLASK'],
  BACKEND_URL_EXPRESS: process.env['BACKEND_URL_EXPRESS'],
  BACKEND_URL_SPRINGBOOT: process.env['BACKEND_URL_SPRINGBOOT'],
  BACKEND_URL_ASPNETCORE: process.env['BACKEND_URL_ASPNETCORE'],
  BACKEND_URL_LARAVEL: process.env['BACKEND_URL_LARAVEL'],
  BACKEND_URL_RUBYONRAILS: process.env['BACKEND_URL_RUBYONRAILS'],
  BACKEND_URL_FLASKOTLP: process.env['BACKEND_URL_FLASKOTLP'],
  BACKEND_URL_SPRINGBOOTOTLP: process.env['BACKEND_URL_SPRINGBOOTOTLP'],
};
