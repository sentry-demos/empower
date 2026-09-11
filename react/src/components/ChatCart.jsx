import React from 'react';

// Cart card, mirroring Cart.jsx's line items and subtotal. Reads the cart the
// agent keeps in its session, which is separate from the site's Redux cart.
function ChatCart({ cart, promo }) {
  if (!cart || !cart.items || cart.items.length === 0) {
    return (
      <div className="chat-widget-card">
        <p className="chat-widget-empty sentry-unmask">Your cart is empty.</p>
      </div>
    );
  }

  return (
    <div className="chat-widget-card" id="chat-cart">
      <ul className="chat-cart-list">
        {cart.items.map((item) => {
          // Quantities come back from JSON, so the keys are strings.
          const quantity = cart.quantities[String(item.id)] || 0;
          return (
            <li className="chat-cart-item" key={item.id}>
              <img
                src={item.imgcropped || item.img}
                alt={item.title}
                className="chat-product-img sentry-block"
              />
              <div className="chat-product-body">
                <span className="chat-product-title">{item.title}</span>
                <span className="chat-product-price sentry-unmask">
                  {quantity} × ${item.price}.00
                </span>
              </div>
              <span className="chat-cart-line-total sentry-unmask">
                ${item.price * quantity}.00
              </span>
            </li>
          );
        })}
      </ul>
      <div className="chat-cart-subtotal">
        <span className="sentry-unmask">Subtotal</span>
        <span className="sentry-unmask" id="chat-cart-total">
          ${cart.total}.00
        </span>
      </div>
      {promo && (
        <div className="chat-cart-promo sentry-unmask">
          Promo {promo.code} applied — {promo.percent_discount}% off
        </div>
      )}
    </div>
  );
}

export default ChatCart;
