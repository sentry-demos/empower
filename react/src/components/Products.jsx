import { Component } from 'react';
import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import { setProducts, addProduct } from '../actions';
import measureRequestDuration from '../utils/measureRequestDuration';
import Loader from 'react-loader-spinner';
import ProductCard from './ProductCard';
import { useState, useEffect } from 'react';

function Products({ frontendSlowdown, backend }) {
  const [products, setProducts] = useState([]);

  function determineProductsEndpoint() {
    return frontendSlowdown ? '/products-join' : '/products';
  }

  function fetchUncompressedAsset() {
    let se; // `se` is automatically added to all fetch requests, but need to do manually for script tags
    Sentry.withScope(function (scope) { se = scope._tags.se; });

    let uc_small_script = document.createElement('script');
    uc_small_script.async = false;
    uc_small_script.src =
      backend +
      '/compressed_assets/compressed_small_file.js' +
      `?cacheBuster=${Math.random()}&se=${se}`; 
    document.body.appendChild(uc_small_script);

    // big uncompressed file
    let c_big_script = document.createElement('script');
    c_big_script.async = false;

    c_big_script.src =
      backend +
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
  async function getProducts(frontendSlowdown) {
    [('/api', '/connect', '/organization')].forEach((endpoint, activeSpan) => {
      fetch(backend + endpoint, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      }).catch((err) => {
        // If there's an error, it won't stop the Products http request and page from loading
        Sentry.captureException(err);
      });
    });
    const productsEndpoint = determineProductsEndpoint();
    Sentry.startSpan({ name: "Fetch Products"}, async (span) => {
      const stopMeasurement = measureRequestDuration(productsEndpoint, span);
      const response = await fetch(backend + productsEndpoint, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();

      if (!response.ok) {
        Sentry.setContext('err', {
          status: response.status,
          statusText: response.statusText,
        });
        return;
      }
      renderProducts(data);
      stopMeasurement();
    })
  }

  useEffect(() => {
     try {
      getProducts(frontendSlowdown)
     } catch (error) {
      Sentry.captureException(error)
     }
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
    <div className="loader-container">
      <Loader type="ThreeDots" color="#f6cfb2" height={150} width={150} />
    </div>
  );
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products,
  };
};

export default connect(mapStateToProps, { setProducts, addProduct })(
  Sentry.withProfiler(Products, { name: 'Products' })
);
