import React, { useEffect, useState, useContext } from 'react';
import { Context } from '../index';
import './product.css';

const Product = ({ match }) => {
  const [product, setProduct] = useState(null);
  const { cart } = useContext(Context);

  useEffect(() => {
    (async () => {
      if (match.params.id) {
        const data = await import(`./products/${match.params.id}`);
        setProduct(data.default);
      }
    })();
  }, [match.params.id]);

  return product ? (
    <div className="product-layout">
      {/* <pre>{JSON.stringify(product, null, 2)}</pre> */}

      <div>
        <img src="https://via.placeholder.com/1000x800" alt="product" />
      </div>
      <div className="product-info">
        <h1>{product.title}</h1>
        <p>{product.description}</p>
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
};

export default Product;
