import './complete.css';
import { Link } from 'react-router-dom';

function NotEnoughInventory() {
  return (
    <div className="not-enough-inventory">
      <h2>Not Enough Inventory</h2>
      <p>
        The product you are interested is out of stock.Please accept our deepest
        apologies. If you want to know when it will be available, please <Link to="/">contact us</Link>.
      </p>
    </div>
  );
}

export default NotEnoughInventory;
