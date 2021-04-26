import { useContext } from 'react';
import { Context } from '../index';
import { Link } from 'react-router-dom';
import './products.css';

import Button from './Button';

function Products(props) {
  const { cart, products } = useContext(Context);
  return (
    <div>
      <ul className="products-list">
        {products.map((product) => {
          const itemLink = '/product/' + product.id;
          return (
            <li key={product.id}>
              <div>
                <Link to={itemLink}>
                  <img src={product.img} alt="product" />
                  <div>
                    <h2>{product.title}</h2>
                    <p className="product-description">{product.description}</p>
                  </div>
                </Link>
                <Button onClick={() => cart.update({ action: 'add', product })}>
                  Add to cart — ${product.price}.00
                </Button>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default Products;
