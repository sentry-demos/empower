// Development environment configuration for Angular
// This file is used by ng serve (development mode)
// Focuses on UI development with minimal backend dependency

export const environment = {
  production: false,
  
  flaskBackend: 'http://localhost:8080',  // Local development - start backend separately if needed
  
  laravelBackend: 'http://localhost:8000', // Local development - start backend separately if needed
  
  sentry: {
    dsn: '',  // Disabled for development
    environment: 'local',
    release: 'dev',
  }
};
