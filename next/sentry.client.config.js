// This file configures the initialization of Sentry on the client.
// The config you add here will be used whenever a users loads a page in their browser.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from '@sentry/nextjs';

const tracingOrigins = [
  'localhost',
  'empowerplant.io',
  'run.app',
  'appspot.com',
  /^\//,
  window.location.host,
];
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_DSN,
  tracesSampleRate: 1.0,
  tracePropagationTargets: tracingOrigins,
  profilesSampleRate: 1.0,
  replaysSessionSampleRate: 1.0,
  debug: false,
  integrations: [
    Sentry.browserProfilingIntegration,
    Sentry.replayIntegration({
      // Additional configuration goes in here
      // replaysSessionSampleRate and replaysOnErrorSampleRate is now a top-level SDK option
      blockAllMedia: false,
      // https://docs.sentry.io/platforms/javascript/session-replay/configuration/#network-details
      networkDetailAllowUrls: ['/checkout', '/products', '/products-sc'],
      unmask: ['.sentry-unmask'],
    }),
  ],
  beforeSend(event, hint) {
    // Parse from tags because src/index.js already set it there. Once there are React route changes, it is no longer in the URL bar
    let se;
    Sentry.withScope(function (scope) {
      se = scope._tags.se;
    });

    if (se) {
      const seTdaPrefixRegex = /[^-]+-tda-[^-]+-/;
      let seFingerprint = se;
      let prefix = seTdaPrefixRegex.exec(se);
      if (prefix) {
        // Now that TDA puts platform/browser and test path into SE tag we want to prevent
        // creating separate issues for those. See https://github.com/sentry-demos/empower/pull/332
        seFingerprint = prefix[0];
      }

      event.fingerprint = ['{{ default }}', seFingerprint];
    }

    if (event.exception) {
      sessionStorage.setItem('lastErrorEventId', event.event_id);
    }

    return event;
  },
});
