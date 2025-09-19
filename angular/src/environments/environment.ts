// Environment configuration for Angular
// Uses webpack DefinePlugin for production builds

export const environment = {
  production: false,
  
  flaskBackend: process.env['ANGULAR_APP_FLASK_BACKEND'] as string,
  
  laravelBackend: process.env['ANGULAR_APP_LARAVEL_BACKEND'] as string,
  
  sentry: {
    dsn: process.env['ANGULAR_APP_DSN'] as string,
    environment: process.env['ANGULAR_APP_ENVIRONMENT'] as string,
    release: process.env['ANGULAR_APP_RELEASE'] as string,
  }
};
