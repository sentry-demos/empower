import { Link } from 'react-router-dom';
import './complete.css';
import { useEffect, useState } from 'react';
import { connect } from 'react-redux';
import * as Sentry from '@sentry/react';
import { resetCart } from '../actions';

function Complete({cart, resetCart}) {
  const [orderedCart] = useState(cart);

  useEffect(() => {
    resetCart();
    
    window.setTimeout(() => {
      Sentry.getReplay().flush();
    }, 1000);
  }, [resetCart]);

  const RandomNumber = Math.floor(Math.random() * 99999) + 10000;

  return (
    <div className="checkout-container-complete">
      <h2>Checkout complete</h2>
      <h4>
        Order No: {RandomNumber} — Total: ${orderedCart.total}.00
      </h4>
      <p>A confirmation email has been sent to the address you provided.</p>
      <p>
        Your plants will thank you. You can <Link to="/">track your order</Link>{' '}
        or <Link to="/">contact us</Link> if you have any questions. Have a
        sunny day.
      </p>
    </div>
  );
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products,
  };
};

export default connect(mapStateToProps, { resetCart })(
  Sentry.withProfiler(Complete, { name: 'Complete' })
);
