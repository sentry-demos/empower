import React, { useState } from 'react';

// Compact checkout form inside the chat.
//
// The agent prefills this server-side (session.form, same defaults as
// CheckoutForm.jsx) and owns the values it sends to /checkout. The inputs here
// are editable so Session Replay shows a real form being filled rather than a
// static block — but note that edits are currently local only: purchase() reads
// the agent's session form, so changing a field here does not change the order.
// Wiring that through needs an update_checkout_form tool.
const FIELDS = [
  { name: 'email', label: 'Email', mask: true },
  { name: 'firstName', label: 'First name', mask: true },
  { name: 'lastName', label: 'Last name', mask: true },
  { name: 'address', label: 'Address', mask: true },
  { name: 'city', label: 'City', mask: true },
  { name: 'zipCode', label: 'ZIP', mask: true },
  { name: 'promoCode', label: 'Promo code', mask: false },
];

// Same check as CheckoutForm.jsx:17 — under TDA the fields start empty so the
// synthetic driver types into them and the replay looks like a real customer.
const seTdaPrefixRegex = /[^-]+-tda-[^-]+-/;

function initialValues(form) {
  const se = sessionStorage.getItem('se');
  if (se && seTdaPrefixRegex.test(se)) {
    return FIELDS.reduce((acc, field) => ({ ...acc, [field.name]: '' }), {});
  }
  return FIELDS.reduce(
    (acc, field) => ({ ...acc, [field.name]: (form && form[field.name]) || '' }),
    {}
  );
}

function ChatCheckout({ form, cart }) {
  const [values, setValues] = useState(() => initialValues(form));

  return (
    <div className="chat-widget-card" id="chat-checkout">
      <span className="chat-checkout-title sentry-unmask">Checkout</span>
      <div className="chat-checkout-fields">
        {FIELDS.map((field) => (
          <label className="chat-checkout-field" key={field.name}>
            <span className="chat-checkout-label sentry-unmask">
              {field.label}
            </span>
            <input
              id={`chat-checkout-${field.name}`}
              type="text"
              className={`chat-checkout-input ${
                field.mask ? 'sentry-block' : 'sentry-unmask'
              }`}
              value={values[field.name]}
              onChange={(e) =>
                setValues((prev) => ({ ...prev, [field.name]: e.target.value }))
              }
            />
          </label>
        ))}
      </div>
      {cart && (
        <div className="chat-cart-subtotal">
          <span className="sentry-unmask">Order total</span>
          <span className="sentry-unmask">${cart.total}.00</span>
        </div>
      )}
    </div>
  );
}

export default ChatCheckout;
