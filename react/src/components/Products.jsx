import { Component } from 'react';
import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import { setProducts, addProduct } from '../actions';
import measureRequestDuration from '../utils/measureRequestDuration';
import Loader from 'react-loader-spinner';
import ProductCard from './ProductCard';
import { useState, useEffect } from 'react';
import { updateStatsigUserAndEvaluate } from '../utils/statsig';

function Products({ backend, productsApi, productsExtremelySlow, productsBeError, addToCartJsError }) {
  const [products, setProducts] = useState([]);

  function renderProducts(data) {
    try {
      console.log('setting products quickly');
      setProducts(data.slice(0, 4));
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
  async function getProducts() {
    [('/api', '/connect', '/organization')].forEach((endpoint, activeSpan) => {
      fetch(backend + endpoint, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      }).catch((err) => {
        // If there's an error, it won't stop the Products http request and page from loading
        Sentry.captureException(err);
      });
    });
    let productsEndpoint = '/products';
    if (productsApi === 'products-join') {
      productsEndpoint = '/products-join';
    } else if (productsExtremelySlow) {
      productsEndpoint = '/products?fetch_promotions=true';
    } else if (productsBeError) {
      productsEndpoint = '/products?in_stock_only=1';
    }
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
      getProducts()
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
            <ProductCard key={i} product={product} stars={stars} addToCartJsError={addToCartJsError}></ProductCard>
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
