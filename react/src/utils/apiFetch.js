export class ApiError extends Error {
  constructor(status, statusText) {
    super(status + ' - ' + (statusText || 'Internal Server Error'));
    this.status = status;
    this.statusText = statusText;
  }
}

export class NonHttpApiError extends Error {
  constructor(error) {
    super(error.message);
    this.error = error;
  }
}

async function apiFetch(url, options) {
  // add default json header
  options.headers = options.headers || {};
  if (!options.headers['Content-Type']) {
    options.headers['Content-Type'] = 'application/json';
  }

  let response;
  try {
    response = await fetch(url, options);
    if (response.ok) {
      return response.json();
    }
  } catch (err) {
    // if we get an error not related to the http request, we want to capture it differently
    throw new NonHttpApiError(err);
  }
  // must be an api error at this point
  throw new ApiError(response.status, response.statusText);
}

// TODO: add query param argument to construct url
export async function get(url, headers) {
  const options = {
    method: 'GET',
    headers,
  };
  return apiFetch(url, options);
}

export async function post(url, data, options={}) {
  options = {
    ...options,
    method: 'POST',
    body: JSON.stringify(data),
  }
  return apiFetch(url, options);
}
