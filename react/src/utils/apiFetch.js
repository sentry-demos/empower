import * as Sentry from '@sentry/react';

export class ApiError extends Error {
  constructor(status, statusText) {
    statusText = statusText || 'Internal Server Error';
    super(status + ' - ' + statusText);
    this.status = status;
    this.statusText = statusText;
  }
}

export function getSentryContext(error) {
  if (error instanceof ApiError) {
    return {
      type: 'ApiError',
      status: error.status,
      statusText: error.statusText,
      message: error.message,
    };
  }
  return {
    type: 'NonHttpApiError',
    message: error.message,
  };
}

async function apiFetch(url, options) {
  // add default json header
  options.headers = options.headers || {};
  if (!options.headers['Content-Type']) {
    options.headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, options);
  if (!response.ok) {
    Sentry.configureScope(function (scope) {
      Sentry.setContext('error', {
        type: 'ApiError',
        status: response.status,
        statsText: response.statusText || 'Internal Server Error',
      });
    });
    console.trace()
    throw new ApiError(response.status, response.statusText);
  }
  // if json, return json
  if (response.headers['Content-Type'] === 'application/json') {
    return response.json();
  }
  return response;
}

// TODO: add query param argument to construct url
export function get(url, headers) {
  const options = {
    method: 'GET',
    headers,
  };
  return apiFetch(url, options);
}

export function post(url, data, options = {}) {
  options = {
    ...options,
    method: 'POST',
    body: JSON.stringify(data),
  };
  return apiFetch(url, options);
}
