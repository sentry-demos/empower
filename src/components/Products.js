import { useContext } from 'react';
import { Context } from '../index';
import { Link } from 'react-router-dom';
import './products.css';

function Products(props) {
  const { cart, products } = useContext(Context);
  return (
    <div>
      <h1>Products catalog</h1>

      <aside>
        <h3>Cart</h3>
        {cart.items.length > 0 ? (
          <>
            <ul>
              {cart.items.map((item) => {
                const quantity = cart.quantities[item.id];
                return (
                  <li>
                    <h4>
                      {item.title} (x {quantity})
                    </h4>
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
      </aside>

      <hr />

      <ul className="products-list">
        {products.map((product) => {
          return (
            <li>
              <Link to="/product/1">
                <img src="https://via.placeholder.com/500x250" alt="product" />
                <div>
                  <h2>{product.title}</h2>
                  <p className="product-description">{product.description}</p>
                </div>
              </Link>
              <div>
                <p className="price">${product.price}.00</p>
                <button onClick={() => cart.update({ action: 'add', product })}>
                  Add to cart
                </button>
                <button
                  onClick={() => cart.update({ action: 'remove', product })}
                >
                  Remove from cart
                </button>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default Products;
