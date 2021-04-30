import React, { Component } from 'react';
import Context from '../utils/context';
import './product.css';
import * as Sentry from '@sentry/react';

class Product extends Component {
  static contextType = Context;

  constructor() {
    super();
    this.state = {
      product: null,
    };
  }

  async componentDidMount() {
    const { match } = this.props;
    if (match.params.id) {
      const data = await import(`./products/${match.params.id}`);
      this.setState({ product: data.default });
    }
  }

  render() {
    const { product } = this.state;
    const { cart } = this.context;
    return product ? (
      <div className="product-layout">
        {/* <pre>{JSON.stringify(product, null, 2)}</pre> */}

        <div>
          <img src={product.imgCrop} alt="product" />
        </div>
        <div className="product-info">
          <h1>{product.title}</h1>
          <p>{product.description}</p>
          <p>{product.descriptionFull}</p>
          <button
            className="add-cart-btn"
            onClick={() => cart.update({ action: 'add', product })}
          >
            Add to cart — ${product.price}.00
          </button>
        </div>
      </div>
    ) : (
      <p>Loading…</p>
    );
  }
}

export default Product;
