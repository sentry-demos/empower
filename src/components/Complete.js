import { useContext } from 'react';
import Context from '../utils/context';
import { Link } from 'react-router-dom';
import './complete.css';
import * as Sentry from '@sentry/react';

function Complete(props) {
  const { cart } = useContext(Context);
  const RandomNumber = Math.floor(Math.random() * 99999) + 10000;

  return (
    <div className="checkout-container-complete">
      <h2>Checkout complete</h2>
      <h4>
        Order No: {RandomNumber} — Total: ${cart.total}.00
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

export default Complete;
