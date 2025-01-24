
import * as Sentry from '@sentry/react';

/**
 * Measure the duration of a request and send it to Sentry as a custom metric
 * @param {string} endpoint the endpoint that was called
 * @returns {() => void} a function to stop the measurement
 */
export default function measureRequestDuration(endpoint, requestSpan) {
  const start = Date.now();
  
  function stopMeasurement() {
    const end = Date.now();
    const duration = end - start;
    if (requestSpan !== undefined) {
      requestSpan.setAttributes({
        "request.duration": duration,
        "unit": "milisecond",
        "endpoint": endpoint
      })
    }
  }

  return stopMeasurement;
}