import React from 'react';
import * as Sentry from '@sentry/react';

// Compact product cards rendered inside the chat, from the `widget` SSE event
// the search_products tool produces. Deliberately not ProductCard.jsx: that one
// is a Redux-connected grid tile that navigates on click and writes to the
// site's cart. The chat cart lives in the agent session instead, so these cards
// only display — adding happens through the agent, by pill or free text.
function ChatProductList({ products, onAddToCart, disabled }) {
  if (!products || products.length === 0) {
    return (
      <div className="chat-widget-card">
        <p className="chat-widget-empty sentry-unmask">
          No products matched that.
        </p>
      </div>
    );
  }

  return (
    // chat-products-card lets the full view drop this outer container: each
    // product is its own card there, so the wrapper is a box drawn around
    // boxes. The popup keeps it — at that width the list needs the frame.
    <div className="chat-widget-card chat-products-card">
      <ul className="chat-product-list">
        {products.map((product) => (
          <li key={product.id} className="chat-product">
            <img
              src={product.imgcropped || product.img}
              alt={product.title}
              className="chat-product-img sentry-block"
            />
            <div className="chat-product-body">
              <span className="chat-product-title">{product.title}</span>
              <span className="chat-product-price sentry-unmask">
                ${product.price}.00
              </span>
            </div>
            <button
              type="button"
              id={`chat-add-product-${product.id}`}
              className="chat-product-add sentry-unmask"
              disabled={disabled}
              onClick={() => {
                Sentry.metrics.count('chat.cart.add', 1, {
                  attributes: { source: 'chat_product_list', product_id: product.id },
                });
                onAddToCart(product);
              }}
            >
              Add
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ChatProductList;
