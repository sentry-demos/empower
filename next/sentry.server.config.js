// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from '@sentry/nextjs';
import { nodeProfilingIntegration } from '@sentry/profiling-node';

// let ENVIRONMENT;
// if (window.location.hostname === 'localhost') {
//   ENVIRONMENT = 'test';
// } else {
//   // App Engine
//   ENVIRONMENT = 'production';
// }
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_DSN,

  // Define how likely traces are sampled. Adjust this value in production, or use tracesSampler for greater control.
  tracesSampleRate: 1.0,
  profileSessionSampleRate: 1.0,
  replaysSessionSampleRate: 1.0,
  //environment: ENVIRONMENT,
  enableLogs: true,
  profileLifecycle: 'trace',
  integrations: [
    Sentry.consoleLoggingIntegration({ levels: ["log", "warn", "error"] }),
    Sentry.prismaIntegration(),
    nodeProfilingIntegration()
  ],

  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: true,
});
