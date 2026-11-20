import React from 'react';

// Orders card, from the list_orders tool. Statuses are whatever flask stores,
// so an unknown one still renders, just without a colour of its own.
const STATUS_LABELS = {
  processing: 'Processing',
  shipped: 'Shipped',
  delivered: 'Delivered',
  cancel_requested: 'Cancel requested',
  cancelled: 'Cancelled',
};

// flask serialises timestamps as RFC 1123 in GMT, e.g. "Mon, 19 Oct 2026
// 09:03:00 GMT". Formatted in UTC so the date doesn't shift with the viewer.
const formatDate = (created) => {
  const date = new Date(created);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  });
};

export function ChatOrderStatus({ status }) {
  return (
    <span className="chat-order-status sentry-unmask" data-status={status}>
      {STATUS_LABELS[status] || status.replace(/_/g, ' ')}
    </span>
  );
}

function ChatOrders({ orders }) {
  return (
    <div className="chat-widget-card" id="chat-orders">
      <div className="chat-orders-header">
        <span className="chat-confirmation-title sentry-unmask">
          Your orders
        </span>
        <span className="chat-orders-count sentry-unmask">
          {orders.length} {orders.length === 1 ? 'order' : 'orders'}
        </span>
      </div>
      <ul className="chat-orders-list">
        {orders.map((order) => {
          const placed = formatDate(order.created);
          return (
            <li className="chat-orders-item" key={order.id}>
              <div className="chat-orders-top">
                <span className="chat-orders-id sentry-unmask">
                  Order #{order.id}
                </span>
                <ChatOrderStatus status={order.status} />
              </div>
              {placed && (
                <span className="chat-orders-date sentry-unmask">
                  Placed {placed}
                </span>
              )}
              <div className="chat-orders-bottom">
                <ul className="chat-orders-items">
                  {order.items.split(', ').map((line) => (
                    <li className="sentry-unmask" key={line}>
                      {line}
                    </li>
                  ))}
                </ul>
                <span className="chat-orders-total sentry-unmask">
                  ${order.total}.00
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default ChatOrders;
