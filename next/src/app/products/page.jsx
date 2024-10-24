'use client'

import * as Sentry from '@sentry/nextjs';
import { connect } from 'react-redux';
import { setProducts, addProduct } from '/src/actions';
import measureRequestDuration from '/src/utils/measureRequestDuration';
import ThreeDotLoader from '/src/ui/ThreeDotLoader'
import ProductCard from '/src/components/ProductCard';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  determineBackendType,
  determineBackendUrl,
} from '/src/utils/backendrouter';

function Products() {
  const { backend,
    frontendSlowdown,
    se,
    productsExtremelySlow,
    productsBeError } = useSearchParams();
  const backendType = determineBackendType(backend);
  const backendUrl = determineBackendUrl(backendType);
  const [products, setProducts] = useState([]);

  function determineProductsEndpoint() {
    if (productsExtremelySlow) {
      return '/products?fetch_promotions=true';
    } else if (productsBeError) {
      return '/products?in_stock_only=1';
    } else {
      return frontendSlowdown ? '/products-join' : '/products';
    }
  }

  function determineProductsEndpoint() {
    return frontendSlowdown ? '/products-join' : '/products';
  }

  function fetchUncompressedAsset() {

    let uc_small_script = document.createElement('script');
    uc_small_script.async = false;
    uc_small_script.src =
      backendUrl +
      '/compressed_assets/compressed_small_file.js' +
      `?cacheBuster=${Math.random()}&se=${se}`;
    document.body.appendChild(uc_small_script);

    // big uncompressed file
    let c_big_script = document.createElement('script');
    c_big_script.async = false;

    c_big_script.src =
      backendUrl +
      '/uncompressed_assets/uncompressed_big_file.js' +
      `?cacheBuster=${Math.random()}&se=${se}`;
    document.body.appendChild(c_big_script);
  }

  // intentionally supposed to be slow
  function renderProducts(data) {
    try {
      // Trigger a Sentry 'Performance Issue' in the case of
      // a frontend slowdown
      if (frontendSlowdown) {
        // Must bust cache to have force transfer size
        // small compressed file
        fetchUncompressedAsset();

        console.log('triggering slow render problem');
        // When triggering a frontend-only slowdown, cause a slow render problem
        setProducts(
          Array(150) // 150 is arbitrary to make a slow enough render
            .fill(data.slice(0, 4))
            .flat()
            .map((p, n) => {
              p.id = n;
              return p;
            })
        );
      } else {
        console.log('setting products quickly');
        setProducts(data.slice(0, 4));
      }
    } catch (err) {
      Sentry.captureException(new Error('app unable to load products: ' + err));
    }
  }

  /*
    Fetching and setting the products used to be done in an
    async componentDidMount function. We have (Nov 2023) changed the way of
    doing this to be non-async, because the async function was getting minified in the
    relevant browser profiling frame, and this made it hard to showcase profiling.

    Jonas B explained why switching away from async function helped:
    "I think what you are seeing is unrelated to hooks and probably
    related to the async keyword + babel transform, hence why it probably got
    fixed with hooks (no transform on that class method anymore)"
  */
  useEffect(() => {
    // getProducts handles error responses differently, depending on the browser used
    function getProducts(frontendSlowdown) {
      [('/api', '/connect', '/organization')].forEach((endpoint) => {
        fetch(backendUrl + endpoint, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }).catch((err) => {
          // If there's an error, it won't stop the Products http request and page from loading
          Sentry.captureException(err);
        });
      });

      // When triggering a frontend-only slowdown, use the products-join endpoint
      // because it returns product data with a fast backend response.
      // Otherwise use the /products endpoint, which provides a slow backend response.
      const productsEndpoint = determineProductsEndpoint();
      const stopMeasurement = measureRequestDuration(productsEndpoint);
      fetch(backendUrl + productsEndpoint, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })
        .then((result) => {
          if (!result.ok) {
            Sentry.setContext('err', {
              status: result.status,
              statusText: result.statusText,
            });
            return Promise.reject();
          } else {
            return result.json();
          }
        })
        .then(renderProducts)
        .catch((err) => {
          return { ok: false, status: 500 };
        })
        .then((res) => {
          stopMeasurement();
          return res;
        });
    }

    getProducts(frontendSlowdown);
  }, []);
  return products.length > 0 ? (
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
  ) : (
    <ThreeDotLoader />
  );
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products,
  };
};

export default connect(mapStateToProps, { setProducts, addProduct })(
  // Disable profiling for vercel deploy
  // Sentry.withProfiler(Products, { name: 'Products' })
  Products
);
