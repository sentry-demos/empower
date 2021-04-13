import { useContext } from 'react';
import { Context } from '../index';
import { Link } from 'react-router-dom';
import './cart.css';

function Checkout(props) {
  const { cart } = useContext(Context);
  return (
    <div className="cart-container">
      <h3>Cart</h3>
      {cart.items.length > 0 ? (
        <>
          <ul>
            {cart.items.map((item) => {
              const quantity = cart.quantities[item.id];
              const itemLink = '/product/' + item.id;
              return (
                <li className="cart-item">
                  <Link to={itemLink}>
                    <h4>{item.title}</h4>
                  </Link>
                  <p>${item.price}</p>
                  <div>
                    {/* TODO: @cameronmcefee these two buttons should incrementally add or remove the item */}
                    <button className="add-cart-btn" onClick={() => {}}>
                      +
                    </button>
                    <span>{quantity}</span>
                    <button onClick={() => {}}>–</button>
                  </div>
                  <p>${item.price * quantity}</p>
                </li>
              );
            })}
          </ul>
          <p>Cart Subtotal: ${cart.total}</p>
          <Link to="/checkout">
            <h4>Proceed to checkout</h4>
          </Link>
        </>
      ) : (
        <p>Please add items to the cart</p>
      )}
    </div>
  );
}

export default Checkout;
