"use client"

import * as Sentry from '@sentry/nextjs';

import { useSearchParams } from 'next/navigation';
import { Fragment } from 'react';
import Link from 'next/link';
import { useState } from 'react';

function Footer() {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const searchParams = useSearchParams();
  const errorBoundary = searchParams.get('error_boundary');

  const handleSubmit = (event) => {
    console.log("error boundary = ", errorBoundary);
    event.preventDefault();
    console.log('Email:', email);
    setSubscribed(true);
    if (errorBoundary !== 'true') {
      addToQueue(email);
    }
  };


  const addToQueue = async (email) => {
    try {
      const resp = await fetch(`/api/enqueue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
      const data = await resp.json();
      console.log(data);
    } catch (err) {
      console.error('Error adding to queue:', err);
    }
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
            <form action={handleSubmit}>
              <label htmlFor="email-subscribe" className="sentry-unmask">
                Email
              </label>
              <input
                type="email"
                name="email-subscribe"
                id="email-subscribe"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              ></input>
            </form>
            <input
              name="email"
              type="submit"
              value="Subscribe"
              className="sentry-unmask"
              onClick={handleSubmit}
            />
            {subscribed && (errorBoundary === 'true' ? <SubscribedMessageError /> : <SubscribedMessage />)}
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
  return <p>You have successfully subscribed!</p>;
}

function SubscribedMessageError() {
  throw new Error('SubscribedMessage error');
}

export default Footer;
