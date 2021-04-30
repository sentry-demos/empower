import { Component } from 'react';
import Context from '../utils/context';
import { Link } from 'react-router-dom';
import './products.css';

class Products extends Component {
  static contextType = Context;
  render() {
    const { cart, products } = this.context;
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
                      <p className="product-description">
                        {product.description}
                      </p>
                    </div>
                  </Link>
                  <button
                    onClick={() => cart.update({ action: 'add', product })}
                  >
                    Add to cart — ${product.price}.00
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    );
  }
}

export default Products;
