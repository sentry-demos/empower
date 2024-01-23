import { Link } from 'react-router-dom';
import './nav.css';
import * as Sentry from '@sentry/react';

import { connect } from 'react-redux';
import { resetCart, addProduct, setProducts } from '../actions';

import EPlogo from '../assets/empowerplant-logo.svg';

function Nav({ cart, frontendSlowdown }) {
  return (
    <>
      <nav id="top-nav" className="show-mobile">
        <div className="nav-contents">
          <Link to="/" id="home-link">
            <img src={EPlogo} className="logo sentry-unmask" alt="logo" />
          </Link>

          <div id="top-right-links">
            <Link to="/about" className="sentry-unmask">
              About
            </Link>
            <Link to="/products" className="sentry-unmask">
              Products
            </Link>
            <Link to="/cart" className="sentry-unmask">
              Cart
              {cart.items.length > 0 ? (
                <span>
                  <span className="sentry-unmask"> ($</span>
                  <span className="sentry-mask">{cart.total}.00</span>
                  <span className="sentry-unmask">)</span>
                </span>
              ) : (
                ''
              )}
            </Link>
          </div>
        </div>
      </nav>

      <nav id="top-nav" className="show-desktop">
        <div className="nav-contents">
          <Link to="/" id="home-link" className="sentry-unmask">
            <img src={EPlogo} className="logo sentry-unmask" alt="logo" />
            Empower Plant
          </Link>

          <div id="top-right-links">
            <Link to="/about" className="sentry-unmask">
              About
            </Link>
            <Link
              to={frontendSlowdown ? '/products-fes' : '/products'}
              className="sentry-unmask"
            >
              Products
            </Link>
            <Link to="/cart">
              <span className="sentry-unmask">Cart</span>
              {cart.items.length > 0 ? (
                <span>
                  <span className="sentry-unmask"> ($</span>
                  <span className="sentry-mask">{cart.total}.00</span>
                  <span className="sentry-unmask">)</span>
                </span>
              ) : (
                ''
              )}
            </Link>
          </div>
        </div>
      </nav>
    </>
  );
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products,
  };
};

export default connect(mapStateToProps, { resetCart, addProduct, setProducts })(
  Sentry.withProfiler(Nav, { name: 'Nav' })
);
