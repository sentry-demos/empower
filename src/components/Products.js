import { Link } from 'react-router-dom';

import './products.css';

function Products(props) {
  const addProductToCart = (product) => {
    const newCart = [...props.cart, product];
    props.setCart(newCart);
  };

  return (
    <div>
      <h1>Products Page Here</h1>

      <ul>
        {props.products.map((product) => {
          return (
            <li>
              {product.title}{' '}
              <button onClick={() => addProductToCart(product)}>add</button>
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
