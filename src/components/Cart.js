import { useContext } from 'react';
import { Context } from '../index';
import { Link } from 'react-router-dom';
import './products.css';

function Checkout(props) {
  const { cart } = useContext(Context);
  return (
    <div>
      <h3>Cart</h3>
      {cart.items.length > 0 ? (
        <>
          <ul>
            {cart.items.map((item) => {
              const quantity = cart.quantities[item.id];
              const itemLink = '/product/' + item.id;
              return (
                <li>
                  <Link to={itemLink}>
                    <p>{itemLink}</p>
                    <h4>
                      {item.title} (x {quantity})
                    </h4>
                  </Link>
                  <p>${item.price * quantity}</p>
                </li>
              );
            })}
          </ul>
          <p>Total: ${cart.total}</p>
        </>
      ) : (
        <p>Please add items to the cart</p>
      )}
    </div>
  );
}

export default Checkout;
