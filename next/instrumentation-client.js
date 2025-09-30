// This file configures the initialization of Sentry on the client.
// The config you add here will be used whenever a users loads a page in their browser.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_DSN,
  tracesSampleRate: 1.0,
  tracePropagationTargets: tracingOrigins,
  profilesSampleRate: 1.0,
  replaysSessionSampleRate: 1.0,
  environment: process.env.NEXT_APP_ENVIRONMENT,
  enableLogs: true,
  debug: false,
  integrations: [
    Sentry.consoleLoggingIntegration({ levels: ["log", "warn", "error"] }),
    Sentry.browserProfilingIntegration(),
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

    // making fewer emails so event and user counts for an Issue are not the same
    let array = [
      'a',
      'b',
      'c',
      'd',
      'e',
      'f',
      'g',
      'h',
      'i',
      'j',
      'k',
      'l',
      'm',
      'n',
      'o',
      'p',
      'q',
      'r',
      's',
      't',
      'u',
      'v',
      'w',
      'x',
      'y',
      'z',
    ];
    let a = array[Math.floor(Math.random() * array.length)];
    let b = array[Math.floor(Math.random() * array.length)];
    let c = array[Math.floor(Math.random() * array.length)];
    let email = a + b + c + '@example.com';
    Sentry.setUser({ email: email });