import { Component } from 'react';
import Context from '../utils/context';
import { Link } from 'react-router-dom';
import './products.css';
import * as Sentry from '@sentry/react';

console.log("window.location", window.location)
var BACKEND = ""
if (window.location.hostname === "localhost") {
  BACKEND = "http://localhost:8080"
} else {
  BACKEND = process.env.REACT_APP_BACKEND
}
console.log("BACKEND", BACKEND)

class Products extends Component {
  static contextType = Context;

  async componentDidMount(){
    const { products } = this.context;
    
    let result = await fetch(`${BACKEND}/products`, {
      method: "GET",
    })
      .then(response => { return response.text() })
      .catch((err) => { throw Error(err) })

    console.log('> Products from backend', JSON.parse(result))

    products.update({ action: 'add', response: JSON.parse(result) })
    return result
  }

  render() {
    const { cart, products } = this.context;
    return (
      <div>
        <ul className="products-list">
          {products.response.map((product) => {
            const itemLink = '/product/' + product.id;
            const averageRating = (product.reviews.reduce((a,b) => a + (b["rating"] || 0),0) / 3).toFixed(1)
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
                  <p>{averageRating} Star Rating</p>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    );
  }
}

export default Sentry.withProfiler(Products, { name: "Products"})
