import React from 'react';

// Suggestion chips. The agent derives these server-side from whichever tool ran
// last and sends them on the `pills` SSE event, so the ids below are stable and
// TDA can drive the demo path by id. They are pre-filled prompts, not the only
// way through the flow — the free-text input stays available at all times.
//
// Two shapes, same ids and same click path:
//
//   chips  the row above the input, used in the popup and mid-conversation
//   cards  the large tiles on the full view's empty state
//
// Only one shape renders at a time, so a pill id never appears twice in the DOM.

// Blurbs for the card shape only. Deliberately client-side: the server sends
// {id, label} because the label is the prompt that gets submitted, and padding
// the SSE payload with presentation copy would make the protocol about layout.
const CARD_BLURBS = {
  'chat-pill-show-products': 'Search the catalogue by price, light or care level.',
  'chat-pill-add-all': 'Put what you are looking at into the cart.',
  'chat-pill-checkout': 'Review the order and the prefilled details.',
  'chat-pill-apply-coupon': 'Try a promo code against the order.',
  'chat-pill-purchase': 'Place the order and get a confirmation.',
  'chat-starter-low-light': 'Ask about placement and light levels.',
  'chat-starter-easy-care': 'Get a recommendation for a forgiving plant.',
};

function ChatPills({ pills, onSelect, disabled, variant = 'chips' }) {
  if (!pills || pills.length === 0) return null;

  if (variant === 'cards') {
    return (
      <div className="chat-pill-cards">
        {pills.map((pill) => (
          <button
            key={pill.id}
            id={pill.id}
            type="button"
            className="chat-pill-card sentry-unmask"
            disabled={disabled}
            onClick={() => onSelect(pill)}
          >
            <span className="chat-pill-card-label">{pill.label}</span>
            {CARD_BLURBS[pill.id] && (
              <span className="chat-pill-card-blurb">
                {CARD_BLURBS[pill.id]}
              </span>
            )}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="chat-pills">
      {pills.map((pill) => (
        <button
          key={pill.id}
          id={pill.id}
          type="button"
          className="chat-pill sentry-unmask"
          disabled={disabled}
          onClick={() => onSelect(pill)}
        >
          {pill.label}
        </button>
      ))}
    </div>
  );
}

export default ChatPills;
