import { Link } from 'react-router-dom';
import './cart.css';
import * as Sentry from '@sentry/react';
import Button from './ButtonLink';
import { connect } from 'react-redux';
import { setProducts, addProduct, removeProduct } from '../actions';
import { useEffect } from 'react';

function Cart(props) {
  return (
    <div className="cart-container">
      <h2 className="sentry-unmask">Cart</h2>
      {props.cart.items.length > 0 ? (
        <>
          <ul className="cart-list">
            {props.cart.items.map((item) => {
              const quantity = props.cart.quantities[item.id];
              const itemLink = '/product/' + item.id;
              return (
                <li className="cart-item" key={item.id}>
                  <Link to={itemLink}>
                    <img
                      src={item.img}
                      alt="item-thumbnail"
                      className="sentry-block"
                    />
                  </Link>
                  <Link to={itemLink}>
                    <h4>{item.title}</h4>
                  </Link>
                  <p>
                    <span className="sentry-unmask">$</span>
                    {item.price}.00
                  </p>
                  <div className="quantity-adjust">
                    <button
                      onClick={() => props.removeProduct(item)}
                      className="sentry-unmask"
                    >
                      –
                    </button>
                    <span>{quantity}</span>
                    <button
                      onClick={() => props.addProduct(item)}
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
            {props.total}.00
          </h3>
          <Button to="/checkout" className="sentry-unmask">
            Proceed to checkout
          </Button>
        </>
      ) : (
        <p>Please add items to the cart SDZ2</p>
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
})(Sentry.withProfiler(Cart, { name: 'Cart' }));
