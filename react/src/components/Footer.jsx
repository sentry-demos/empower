import * as Sentry from '@sentry/react';
import { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import './footer.css';

function Footer({ errorBoundary, backend }) {
  const [email, setEmail] = useState('');
  console.log('errorBoundary', errorBoundary);
  const [subscribed, setSubscribed] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubscribed(true);
    addToQueue();
  };

  async function addToQueue() {
    try {
      console.log("Sending to queue...");
      const resp = await fetch(`${backend}/enqueue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await resp.json();
      console.log(data);
    } catch (err) {
      console.error('Error adding to queue:', err);
    }
  }

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
            <form>
              <label htmlFor="email-subscribe" className="sentry-unmask">
                Email
              </label>
              <input
                type="email"
                name="email-subscribe"
                id="email-subscribe"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <button
                type="submit"
                className="subscribe-button sentry-unmask"
                onClick={handleSubmit}
              >
                Subscribe
              </button>
            </form>
            {subscribed && (errorBoundary === 'true' ? <SubscribedMessageError /> : <SubscribedMessage />)}
          </div>
        </Sentry.ErrorBoundary>
        <p className="sentry-unmask">
          © 2021 • Empower Plant • <Link to="/about">About us</Link>
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
