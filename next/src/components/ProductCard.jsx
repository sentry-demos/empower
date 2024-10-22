'use client'

import { useRouter } from 'next/navigation';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import { setProducts, addProduct, setFlag } from '../actions';

function ProductCard(props) {
  const router = useRouter();
  const { query } = router;
  const product = props.product;
  const itemLink = '/product';
  const stars = props.stars;

  return (
    <li key={product.id}>
      <div
        onClick={(event) => {
          if (
            event.target.id !== 'addToCart' &&
            event.target.parentNode.id !== 'addToCart'
          ) {
            router.push({
              pathname: itemLink,
              // TODO how do we push the product object to the next page using router?
              query: { product: product, ...query },
            });
          }
        }}
      >
        <img src={product.img} alt="product" className="sentry-block" />
        <div>
          <h2>{product.title}</h2>
          <p className="product-description">{product.description}</p>
        </div>
        <button id="addToCart" onClick={() => props.addProduct(product)}>
          <span className="sentry-unmask">Add to cart — $</span>
          {product.price}.00
        </button>
        <p>
          {stars} ({product.reviews.length})
        </p>
      </div>
    </li>
  );
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products,
    flag: state.flag,
  };
};

export default connect(mapStateToProps, { setProducts, addProduct, setFlag })(
  ProductCard
);
