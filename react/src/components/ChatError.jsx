import React from 'react';

// Error bubble. The point of the coupon and purchase failures is that the
// customer sees the real backend message, so this renders whatever the agent
// forwarded rather than flattening it into "something went wrong" the way
// CheckoutForm.jsx does with the expired-coupon 410.
function ChatError({ message, code }) {
  return (
    <div className="chat-widget-card chat-error" id="chat-error">
      <span className="chat-error-title sentry-unmask">Something went wrong</span>
      <p className="chat-error-message">{message || 'Unknown error'}</p>
      {code && <span className="chat-error-code">{code}</span>}
    </div>
  );
}

export default ChatError;
