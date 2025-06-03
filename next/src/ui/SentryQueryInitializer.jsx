// @ts-check

'use client';

import React from 'react';

import { useSearchParams } from 'next/navigation';
import * as Sentry from '@sentry/nextjs';
import Cookies from 'js-cookie';

export default function SentryQueryInitializer() {
  const searchParams = useSearchParams();
  const query = Object.fromEntries(searchParams.entries());

  let globalScope = Sentry.getGlobalScope();

  const customerType = [
    'medium-plan',
    'large-plan',
    'small-plan',
    'enterprise',
  ][Math.floor(Math.random() * 4)];
  globalScope.setTag('customerType', customerType);

  if (query.se) {
    // Route components (navigation changes) will now have 'se' tag on scope
    console.log('> src/index.js se', query.se);
    globalScope.setTag('se', query.se);
    // Set se tag as cookie to persist on server runtime
    Cookies.set("se", query.se);
    // for use in Checkout.js when deciding whether to pre-fill form
    // lasts for as long as the tab is open

    // TODO Determine if we need below
    // commenting out because its breaking the server component
    //sessionStorage.setItem('se', query.se);
  }

  if (query.frontendSlowdown === 'true') {
    console.log('> frontend-only slowdown: true');
    globalScope.setTag('frontendSlowdown', true);
  } else {
    console.log('> frontend + backend slowdown');
    globalScope.setTag('frontendSlowdown', false);
  }

  // TODO Determine if we need below
  // commenting out because its breaking the server component
  // if (query.userFeedback) {
  //   sessionStorage.setItem('userFeedback', query.userFeedback);
  // } else {
  //   sessionStorage.setItem('userFeedback', 'false');
  // }
  // sessionStorage.removeItem('lastErrorEventId');

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

  globalScope.setUser({ email: email });

  // TODO Determine if we need below
  // commenting out because its breaking the server component
  //crasher();

  return <></>;
}
