'use client'

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { connect } from 'react-redux';
import { addProduct } from '@/src/actions';
import DOMPurify from 'dompurify';

function Product(props) {
  const [product, setProduct] = useState();

  const router = useRouter();
  //const location = useLocation();

  useEffect(() => {
    const { product } = router.query;
    //const product = location.state;
    setProduct(product);
  }, [product]);

  let averageRating;
  if (product) {
    averageRating = (
      product.reviews.reduce((a, b) => a + (b['rating'] || 0), 0) /
      product.reviews.length
    ).toFixed(1);
  }

  return product ? (
    <div className="product-layout">
      <div>
        <img src={DOMPurify.sanitize(product.imgcropped)} alt="product" />
      </div>
      <div className="product-info">
        <h1>{product.title}</h1>
        <p>{product.description}</p>
        <p>{product.descriptionfull}</p>
        <button
          className="add-cart-btn"
          onClick={() => props.addProduct(product)}
        >
          <span className="sentry-unmask">Add to cart —</span> ${product.price}
          .00
        </button>
        <p>{averageRating} Rating</p>
      </div>
    </div>
  ) : (
    <p>Loading…</p>
  );
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products,
  };
};

export default connect(mapStateToProps, { addProduct })(Product);
