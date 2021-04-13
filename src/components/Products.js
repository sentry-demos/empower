import { useContext } from 'react';
import { Context } from '../index';
import { Link } from 'react-router-dom';
import './products.css';

function Products(props) {
  const { cart, products } = useContext(Context);
  return (
    <div>
      <ul className="products-list">
        {products.map((product) => {
          const itemLink = '/product/' + product.id;
          return (
            <li>
              <div>
                <Link to={itemLink}>
                  <img
                    src="https://via.placeholder.com/500x250"
                    alt="product"
                  />
                  <div>
                    <h2>{product.title}</h2>
                    <p className="product-description">{product.description}</p>
                  </div>
                </Link>
                <button
                  className="add-cart-btn"
                  onClick={() => cart.update({ action: 'add', product })}
                >
                  Add to cart — ${product.price}.00
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
