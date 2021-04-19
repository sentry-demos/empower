import { useContext } from 'react';
import { Context } from '../index';
import { Link } from 'react-router-dom';
import './cart.css';

function Checkout(props) {
  const { cart } = useContext(Context);
  return (
    <div className="cart-container">
      <h2>Cart</h2>
      {cart.items.length > 0 ? (
        <>
          <ul>
            {cart.items.map((item) => {
              const quantity = cart.quantities[item.id];
              const itemLink = '/product/' + item.id;
              return (
                <li className="cart-item" key={item.id}>
                  <Link to={itemLink}>
                    <img src={item.img} alt="item-thumbnail" />
                  </Link>
                  <Link to={itemLink}>
                    <h4>{item.title}</h4>
                  </Link>
                  <p>${item.price}</p>
                  <div className="quantity-adjust">
                    <button
                      onClick={() =>
                        cart.update({ action: 'remove', product: item })
                      }
                    >
                      –
                    </button>
                    <span>{quantity}</span>
                    <button
                      className="add-cart-btn"
                      onClick={() =>
                        cart.update({ action: 'add', product: item })
                      }
                    >
                      +
                    </button>
                  </div>
                  <p>${item.price * quantity}</p>
                </li>
              );
            })}
          </ul>
          <h3 className="cart-subtotal">Cart Subtotal: ${cart.total}</h3>
          <Link to="/checkout" className="btn">
            Proceed to checkout
          </Link>
        </>
      ) : (
        <p>Please add items to the cart</p>
      )}
    </div>
  );
}

export default Checkout;
