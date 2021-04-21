import { useContext } from 'react';
import { Context } from '../index';
import { Link } from 'react-router-dom';
import './complete.css';

function Complete(props) {
  const { cart } = useContext(Context);
  const RandomNumber = Math.floor(Math.random() * 99999) + 10000;

  return (
    <div className="checkout-container-complete">
      <h2>We're having some trouble</h2>
      <p>
        We were unable to process your order but will do everything we can to
        make it right. Please <Link to="/">reach out to us</Link> if you have
        been charged or have any questions.
      </p>
    </div>
  );
}

export default Complete;
