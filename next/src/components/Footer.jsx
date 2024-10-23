"use client"

import * as Sentry from '@sentry/react';
import { Fragment } from 'react';
import Link from 'next/link';
import { useState } from 'react';

function Footer() {
  const [subscribed, setSubscribed] = useState(false);

  const handleSubmit = () => {
    setSubscribed(true);
  };

  return (
    <footer id="footer">
      <div>
        <h2 className="h3 sentry-unmask">Sign up for plant tech news</h2>
        <Sentry.ErrorBoundary
          onReset={() => {
            setSubscribed(false);
          }}
          fallback={({ resetError, eventId }) => {
            return (
              <Fragment>
                <div>An error has occurred. Sentry Event ID: {eventId}</div>
                <button className="btn" onClick={resetError}>
                  Reset Form
                </button>
              </Fragment>
            );
          }}
        >
          <div className="formContainer">
            <form onSubmitCapture={handleSubmit}>
              <label htmlFor="email-subscribe" className="sentry-unmask">
                Email
              </label>
              <input
                type="email"
                name="email-subscribe"
                id="email-subscribe"
              ></input>
            </form>
            <input
              type="submit"
              value="Subscribe"
              className="sentry-unmask"
              onClick={handleSubmit}
            />
            {subscribed && <SubscribedMessage />}
          </div>
        </Sentry.ErrorBoundary>
        <p className="sentry-unmask">
          © 2021 • Empower Plant • <Link href="/about">About us</Link>
        </p>
      </div>
    </footer>
  );
}

function SubscribedMessage() {
  throw new Error('SubscribedMessage error');
}

export default Footer;
