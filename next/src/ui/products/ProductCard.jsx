'use client'

import { useRouter } from 'next/navigation';
import * as Sentry from '@sentry/nextjs';
import { connect } from 'react-redux';
import { setProducts, addProduct, setFlag } from '@/src/actions';

function ProductCard(props) {
  const router = useRouter();
  const product = props.product;
  const stars = props.stars;

  return (
    <li key={product.id}>
      <div
        onClick={(event) => {
            router.push(`/product/${product.id}`);
          }}
      >
        <img src={product.img} alt="product" className="sentry-block" />
        <div>
          <h2>{product.title}</h2>
          <p className="product-description">{product.description}</p>
        </div>
        <button id="addToCart" onClick={(e) => {
          throw new Error('test');
          props.addProduct(product);
          e.stopPropagation();
        }}>
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
