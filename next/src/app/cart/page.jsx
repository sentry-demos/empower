'use client'

import Link from 'next/link';

import Button from '@/src/ui/ButtonLink';
import { connect } from 'react-redux';
import { setProducts, addProduct, removeProduct } from '/src/actions';

function Cart({ cart, removeProduct, addProduct }) {
  return (
    <div className="cart-container">
      <h2 className="sentry-unmask">Cart</h2>
      {cart.items.length > 0 ? (
        <>
          <ul className="cart-list">
            {cart.items.map((item) => {
              const quantity = cart.quantities[item.id];
              const itemLink = {
                pathname: '/product/',
                query: { product: item.id },
              }; // Should this be item and not item.id?

              return (
                <li className="cart-item" key={item.id}>
                  <Link href={itemLink}>
                    <img
                      src={item.img}
                      alt="item-thumbnail"
                      className="sentry-block"
                    />
                  </Link>
                  <Link href={itemLink}>
                    <h4>{item.title}</h4>
                  </Link>
                  <p>
                    <span className="sentry-unmask">$</span>
                    {item.price}.00
                  </p>
                  <div className="quantity-adjust">
                    <button
                      onClick={() => removeProduct(item)}
                      className="sentry-unmask"
                    >
                      –
                    </button>
                    <span>{quantity}</span>
                    <button
                      onClick={() => addProduct(item)}
                      className="sentry-unmask"
                    >
                      +
                    </button>
                  </div>
                  <p>
                    <span className="sentry-unmask">$</span>
                    {item.price * quantity}.00
                  </p>
                </li>
              );
            })}
          </ul>
          <h3 className="cart-subtotal">
            <span className="sentry-unmask">Cart Subtotal: $</span>
            {cart.total}.00
          </h3>
          <Button to="/checkout" className="sentry-unmask">
            Proceed to checkout
          </Button>
        </>
      ) : (
        <p>Please add items to the cart</p>
      )}
    </div>
  );
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products,
  };
};

export default connect(mapStateToProps, {
  setProducts,
  addProduct,
  removeProduct,
})(
  // Disable profiling for vercel deploy
  // Sentry.withProfiler(Cart, { name: 'Cart' })
  Cart
);
