import React, { useEffect, useState } from 'react';

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
    <pre>{JSON.stringify(product, null, 2)}</pre>
  ) : (
    <p>Loading…</p>
  );
};

export default Product;
