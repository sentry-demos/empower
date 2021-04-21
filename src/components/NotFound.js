import './complete.css';
import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="checkout-container-complete">
      <h2>404</h2>
      <p>
        We can't seem to find the page you were just directed to. Please go back
        in your browser or go <Link to="/">back to our home page</Link> and
        accept our deepest apologies.
      </p>
    </div>
  );
}

export default NotFound;
