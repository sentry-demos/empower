import { Link } from 'react-router-dom';
import './complete.css';
import * as Sentry from '@sentry/react';
import { useEffect } from 'react';

function CompleteError() {
  useEffect(() => {
    window.setTimeout(() => {
      if (sessionStorage.getItem('userFeedback') === 'true') {
        sessionStorage.removeItem('userFeedback');
        if (sessionStorage.getItem('lastErrorEventId')) {
          Sentry.showReportDialog({
            eventId: sessionStorage.getItem('lastErrorEventId'),
          });
        } else {
          console.log(
            'No error event id found, not showing User Feedback report dialog'
          );
        }
      }
    }, 3500);
  });

  return (
    <div className="checkout-container-complete sentry-unmask">
      <h2>We're having some trouble</h2>
      <p>
        We were unable to process your order but will do everything we can to
        make it right. Please <Link to="#">reach out to us</Link> if you have
        been charged or have any questions.
      </p>
      <button id="contact-us">Contact Us</button>
    </div>
  );
}

export default CompleteError;
