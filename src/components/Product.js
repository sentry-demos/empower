import React, { useEffect, useState } from 'react';
import './product.css';

const Product = ({ match }) => {
  const [product, setProduct] = useState(null);

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

      <div>image</div>
      <div>
        <hr />
        <h1>{product.title}</h1>
        <p>{product.description}</p>
        <button>Add to cart — ${product.price}.00</button>
      </div>
    </div>
  ) : (
    <p>Loading…</p>
  );
};

export default Product;
