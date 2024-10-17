import * as Sentry from '@sentry/nextjs';

/**
 * Measure the duration of a request and send it to Sentry as a custom metric
 * @param {string} endpoint the endpoint that was called
 * @returns {() => void} a function to stop the measurement
 */
export default function measureRequestDuration(endpoint) {
  const start = Date.now();

  function stopMeasurement() {
    const end = Date.now();
    const duration = end - start;
    Sentry.metrics.distribution('request.duration', duration, {
      unit: 'millisecond',
      tags: { endpoint },
    });
  }

  return stopMeasurement;
}
