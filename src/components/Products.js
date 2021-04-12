import { useContext } from 'react';
import { Context } from '../index';
import { Link } from 'react-router-dom';

import './products.css';

function Products(props) {
  const { cart, products } = useContext(Context);
  return (
    <div>
      <h1>Products Page Here</h1>

      <aside>
        <h3>Cart</h3>
        {cart.items.length > 0 ? (
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
        ) : (
          <p>Please add items to the cart</p>
        )}
      </aside>

      <hr />

      <ul>
        {products.map((product) => {
          return (
            <li>
              {product.title}{' '}
              <button onClick={() => cart.update({ action: 'add', product })}>
                add
              </button>
              <button
                onClick={() => cart.update({ action: 'remove', product })}
              >
                remove
              </button>
            </li>
          );
        })}
      </ul>

      <ul className="products-list">
        <li>
          <Link to="/product/1">
            <img src="https://via.placeholder.com/500x250" alt="product" />
            <div>
              <h2>Item A</h2>
              <p className="product-description">
                Something descriptive about this item.
              </p>
            </div>
            <div>
              <p className="price">$100.00</p>
              <button>Add to cart</button>
            </div>
          </Link>
        </li>

        <li>
          <Link to="/product/2">
            <img src="https://via.placeholder.com/500x250" alt="product" />
            <div>
              <h2>Item B</h2>
              <p className="product-description">
                Something descriptive about this item.
              </p>
            </div>
            <div>
              <p className="price">$100.00</p>
              <button>Add to cart</button>
            </div>
          </Link>
        </li>

        <li>
          <Link to="/product/3">
            <img src="https://via.placeholder.com/500x250" alt="product" />
            <div>
              <h2>Item C</h2>
              <p className="product-description">
                Something descriptive about this item.
              </p>
            </div>
            <div>
              <p className="price">$100.00</p>
              <button>Add to cart</button>
            </div>
          </Link>
        </li>

        <li>
          <Link to="/product/4">
            <img src="https://via.placeholder.com/500x250" alt="product" />
            <div>
              <h2>Item D</h2>
              <p className="product-description">
                Something descriptive about this item.
              </p>
            </div>
            <div>
              <p className="price">$100.00</p>
              <button>Add to cart</button>
            </div>
          </Link>
        </li>
      </ul>
    </div>
  );
}

export default Products;
