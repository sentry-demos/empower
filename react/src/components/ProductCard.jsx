import { useNavigate } from 'react-router-dom';
import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import { setProducts, addProduct, setFlag } from '../actions';

function ProductCard(props) {
  let inventory = [3, 4, 5, 6]
  if (props.addToCartJsError) {
    inventory = undefined
  }

  const navigate = useNavigate();
  const product = props.product;
  const itemLink = '/product/' + product.id;
  const stars = props.stars;

  function validate_inventory(product) {
    try {
      return product && inventory.includes(product.id);
    } catch (error) {
      Sentry.captureException(error);
      return false;
    }
  }

  return (
    <li key={product.id}>
      <div
        onClick={(event) => {
          if (
            event.target.id !== 'addToCart' &&
            event.target.parentNode.id !== 'addToCart'
          ) {
            navigate(itemLink, { state: product });
          }
        }}
      >
        <img src={product.img} alt="product" className="sentry-block" />
        <div>
          <h2>{product.title}</h2>
          <p className="product-description">{product.description}</p>
        </div>
        <button
          id="addToCart"
          onClick={() => {
            if (validate_inventory(product)) {
              props.addProduct(product);
            }
          }}
        >
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
  Sentry.withProfiler(ProductCard, { name: 'ProductCard' })
);
