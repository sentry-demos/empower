// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from '@sentry/nextjs';
import { PrismaInstrumentation } from '@prisma/instrumentation';
import { nodeProfilingIntegration } from '@sentry/profiling-node';

console.log('Sentry.init: ', process.env.NEXT_PUBLIC_DSN);
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_DSN,

  // Define how likely traces are sampled. Adjust this value in production, or use tracesSampler for greater control.
  tracesSampleRate: 1.0,
  profileSessionSampleRate: 1.0,
  profileLifecycle: 'trace',
  

  integrations: [
    Sentry.prismaIntegration({
      // Override the default instrumentation that Sentry uses
      prismaInstrumentation: new PrismaInstrumentation(),
    }),
    nodeProfilingIntegration(),
  ],

  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: false,
});
