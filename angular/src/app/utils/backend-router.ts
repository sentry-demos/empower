// Backend router utility for Angular
// Mirrors React's backendrouter.js functionality
// Handles dynamic backend switching based on URL parameters

import { environment } from '../../environments/environment';

const DEFAULT_BACKEND = 'flask';

// Map of supported backend types to their environment variable URLs
const SUPPORTED_BACKEND_TYPES: { [key: string]: string | undefined } = {
  flask: environment.BACKEND_URL_FLASK,
  express: environment.BACKEND_URL_EXPRESS,
  springboot: environment.BACKEND_URL_SPRINGBOOT,
  aspnetcore: environment.BACKEND_URL_ASPNETCORE,
  laravel: environment.BACKEND_URL_LARAVEL,
  rails: environment.BACKEND_URL_RUBYONRAILS,
};

/**
 * Determines which backend type to use based on user input
 * Falls back to default if invalid backend is requested
 * 
 * @param desiredBackend - The backend type from URL parameter
 * @returns Valid backend type string
 */
export const determineBackendType = (desiredBackend: string | null): string => {
  if (desiredBackend) {
    if (SUPPORTED_BACKEND_TYPES[desiredBackend]) {
      return desiredBackend;
    } else {
      const warnText =
        "You tried to set backend type as '" +
        desiredBackend +
        "', which is not supported. Proceeding with the default type: '" +
        DEFAULT_BACKEND +
        "'";
      alert(warnText);
      console.log(warnText);
    }
  }
  return DEFAULT_BACKEND;
};

/**
 * Gets the backend URL for a given backend type
 * 
 * @param backendType - The backend type (flask, laravel, express, etc.)
 * @returns Backend URL string or undefined if not configured
 */
export const determineBackendUrl = (backendType: string): string | undefined => {
  return SUPPORTED_BACKEND_TYPES[backendType];
};
