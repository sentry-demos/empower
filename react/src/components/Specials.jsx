import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import { setProducts, addProduct } from '../actions';
import Loader from 'react-loader-spinner';
import ProductCard from './ProductCard';
import { useState, useEffect } from 'react';

function Specials({ backend }) {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch(backend + '/get_specials', {
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
      .then((data) => setProducts(data))
      .catch((err) => {
        return { ok: false, status: 500 };
      });
  }, []);

  return (
    <div>
      <h1 className="sentry-unmask" style={{ textAlign: 'center', marginBottom: '2rem' }}>Special Offers</h1>
      {products.length > 0 ? (
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
      ) : (
        <div className="loader-container">
          <Loader type="ThreeDots" color="#f6cfb2" height={150} width={150} />
        </div>
      )}
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
  Sentry.withProfiler(Specials, { name: 'Specials' })
); 