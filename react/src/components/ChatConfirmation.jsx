import React from 'react';

// Order confirmation card, rendered from the purchase tool's output on the
// success path. The failure path renders ChatError instead.
function ChatConfirmation({ orderTotal, itemCount }) {
  return (
    <div className="chat-widget-card chat-confirmation" id="chat-confirmation">
      <span className="chat-confirmation-title sentry-unmask">
        Order placed
      </span>
      <p className="chat-confirmation-body sentry-unmask">
        {itemCount} item{itemCount === 1 ? '' : 's'} · ${orderTotal}.00
      </p>
    </div>
  );
}

export default ChatConfirmation;
