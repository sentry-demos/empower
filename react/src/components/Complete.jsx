import { Link } from 'react-router-dom';
import './complete.css';
import { useSelector } from 'react-redux';

function Complete({cart, resetCart}) {
  const cart = useSelector((state) => state.cart);

  useEffect(() => {
    window.setTimeout(() => {
      Sentry.getReplay().flush();
    }, 1000);
  });

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
