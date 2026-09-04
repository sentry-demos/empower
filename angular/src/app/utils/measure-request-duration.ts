import * as Sentry from '@sentry/angular';
import { metrics } from '@sentry/browser';

export function measureRequestDuration(endpoint: string, requestSpan?: Sentry.Span): () => void {
  const start = Date.now();

  function stopMeasurement(): void {
    const end = Date.now();
    const duration = end - start;
    if (requestSpan !== undefined) {
      requestSpan.setAttributes({
        'request.duration': duration,
        'unit': 'millisecond',
        'endpoint': endpoint
      });
    }
    metrics.distribution('request.duration', duration, {
      unit: 'millisecond',
      attributes: { endpoint },
    });
  }

  return stopMeasurement;
}
