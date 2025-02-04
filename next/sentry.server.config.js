// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: 'https://b9943feb5e210fbd4de6a8871d9f1db4@o88872.ingest.us.sentry.io/4508135114014720',

  // Define how likely traces are sampled. Adjust this value in production, or use tracesSampler for greater control.
  tracesSampleRate: 1,

  integrations: [Sentry.prismaIntegration()],

  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: false,
});
