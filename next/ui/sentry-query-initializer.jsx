'use client'

import React from "react";
import { crasher } from '/src/utils/errors';

import { useSearchParams } from 'next/navigation';
import * as Sentry from '@sentry/nextjs';
import {
  determineBackendType,
  determineBackendUrl,
} from '/src/utils/backendrouter';

// Why does this component exist?
// Layouts do not recieve searchParams: https://nextjs.org/docs/app/api-reference/file-conventions/layout#layouts-do-not-receive-searchparams
// However, empower plant app requires these params to initialize sentry, setup the backend, etc.
// This component is a workaround to pull the params into the root layout.jsx so the instances exist on all pages

const inDevEnvironment = !!process && process.env.NODE_ENV === 'development';

export default function SentryQueryInitializer() {
  const tracingOrigins = [
    'localhost',
    'empowerplant.io',
    'run.app',
    'appspot.com',
    /^\//,
  ];

  let ENVIRONMENT;
  // if (window.location.hostname === 'localhost') {
  //   ENVIRONMENT = 'test';
  // } else {
  //   // App Engine
  //   ENVIRONMENT = 'production';
  // }

  let BACKEND_URL;
  let FRONTEND_SLOWDOWN;
  let RAGECLICK;
  const DSN = process.env.NEXT_PUBLIC_DSN;
  const RELEASE = process.env.NEXT_PUBLIC_RELEASE;


  function initSentry(environment) {
    Sentry.init({
      dsn: DSN,
      release: RELEASE,
      environment: environment,
      tracesSampleRate: 1.0,
      tracePropagationTargets: tracingOrigins,
      profilesSampleRate: 1.0,
      replaysSessionSampleRate: 1.0,
      debug: true,
      defaultIntegrations: false,
      integrations: [],
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
          if (se.startsWith('prod-tda-')) {
            // Release Health
            event.fingerprint = ['{{ default }}', seFingerprint, RELEASE];
          } else {
            // SE Testing
            event.fingerprint = ['{{ default }}', seFingerprint];
          }
        }

        if (event.exception) {
          sessionStorage.setItem('lastErrorEventId', event.event_id);
        }

        return event;
      },
    });
  }

  const searchParams = useSearchParams();
  const query = Object.fromEntries(searchParams.entries());

  // Set the environment based on the host
  const environment = inDevEnvironment ? 'test' : 'production';
  initSentry(environment);

  const backendType = determineBackendType('');
  BACKEND_URL = determineBackendUrl(backendType, ENVIRONMENT);
  console.log(`> backendType: ${backendType} | backendUrl: ${BACKEND_URL}`);

  // These also get passed via request headers (see window.fetch below)

  // NOTE: because the demo extracts tags from the scope in order to pass them
  // as headers to the backend, we need to make sure we are calling `setTag()`
  // on the current scope. We don't want to call Sentry.setTag() as is usually
  // recommended (https://docs.sentry.io/platforms/javascript/enriching-events/scopes/#isolation-scope),
  // because that would set the tag on the isolation scope, and make it inaccessible
  // when it's time to set the headers.
  let currentScope = Sentry.getCurrentScope();

  const customerType = [
    'medium-plan',
    'large-plan',
    'small-plan',
    'enterprise',
  ][Math.floor(Math.random() * 4)];
  currentScope.setTag('customerType', customerType);

  if (query.se) {
    // Route components (navigation changes) will now have 'se' tag on scope
    console.log('> src/index.js se', query.se);
    currentScope.setTag('se', query.se);
    // for use in Checkout.js when deciding whether to pre-fill form
    // lasts for as long as the tab is open
    sessionStorage.setItem('se', query.se);
  }

  if (query.frontendSlowdown === 'true') {
    console.log('> frontend-only slowdown: true');
    FRONTEND_SLOWDOWN = true;
    currentScope.setTag('frontendSlowdown', true);
  } else {
    console.log('> frontend + backend slowdown');
    currentScope.setTag('frontendSlowdown', false);
  }

  if (query.rageclick === 'true') {
    RAGECLICK = true;
  }

  if (query.userFeedback) {
    sessionStorage.setItem('userFeedback', query.userFeedback);
  } else {
    sessionStorage.setItem('userFeedback', 'false');
  }
  sessionStorage.removeItem('lastErrorEventId');

  currentScope.setTag('backendType', backendType);

  let email = null;
  if (query.userEmail) {
    email = query.userEmail;
  } else {
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
    email = a + b + c + '@example.com';
  }
  currentScope.setUser({ email: email });
  crasher();

  return (
    <></>
  );
}
