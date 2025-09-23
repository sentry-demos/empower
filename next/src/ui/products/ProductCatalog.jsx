
import React from 'react';
import ProductCard from '@/src/ui/products/ProductCard';
import { getProductsRaw } from '@/lib/data.js';
import { vercelWaitUntil } from '@sentry/core';

export default async function ProductCatalog(props) {

  let products = await getProductsRaw();
  // Removed 2-second artificial delay that was causing profiling timeouts
  // vercelWaitUntil(new Promise(resolve => setTimeout(resolve, 2000)));

  return (
    <div>
      <ul className="products-list">
        {products.map((product, i) => {
          const averageRating = (
            product.reviews.reduce((a, b) => a + (b['rating'] || 0), 0) /
            product.reviews.length
          ).toFixed(1);

          let stars = [1, 2, 3, 4, 5].map((index) => {
            if (index <= averageRating) {
              return (
                <span className="star" key={index}>
                  &#9733;
                </span>
              );
            } else {
              return (
                <span className="star" key={index}>
                  &#9734;
                </span>
              );
            }
          });

          return (
            <ProductCard key={i} product={product} stars={stars}></ProductCard>
          );
        })}
      </ul>
    </div>
  )
}
