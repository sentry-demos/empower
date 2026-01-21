import { feedbackIntegration, handleErrorWithSentry, replayIntegration } from '@sentry/sveltekit';
import * as Sentry from '@sentry/sveltekit';

Sentry.init({
	dsn: 'https://48120459f75f9fe2d3d62228feec6c41@o87286.ingest.us.sentry.io/4509011720863745',

	tracePropagationTargets: ['localhost', 'empower-plant.com', 'run.app', 'appspot.com', /^\//],

	tracesSampleRate: 1.0,
	replaysSessionSampleRate: 0.1,
	replaysOnErrorSampleRate: 1.0,
	integrations: [replayIntegration(), feedbackIntegration()]
});

// If you have a custom error handler, pass it to `handleErrorWithSentry`
export const handleError = handleErrorWithSentry();
