import { Link } from 'react-router-dom';
import './checkout.css';

function Checkout() {
  return (
    <div className="checkout-container">
      <h2>Checkout</h2>
      <div className="checkout-form">form goes here</div>
      <Link to="/cart">Back to cart</Link>
      <button className="complete-checkout-btn">Complete order</button>
    </div>
  );
}

export default Checkout;
