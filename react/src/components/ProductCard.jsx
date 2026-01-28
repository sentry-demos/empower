import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import { setProducts, addProduct, setFlag } from '../actions';

function ProductCard(props) {
  const [categoryData, setCategoryData] = useState(null);

  let inventory = [3, 4, 5, 6]
  if (props.addToCartJsError) {
    inventory = undefined
  }

  const navigate = useNavigate();
  const product = props.product;
  const itemLink = '/product/' + product.id;
  const stars = props.stars;
  const backend = props.backend;

  // Fetch category metadata for badge styling
  useEffect(() => {
    async function fetchCategoryData() {
      try {
        const response = await fetch(`${backend}/api/categories/${product.category.id}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        if (response.ok) {
          const data = await response.json();
          setCategoryData(data);
        }
      } catch (err) {
        Sentry.captureException(err);
      }
    }
    fetchCategoryData();
  }, [product.category.id, backend]);

  const categoryBadge = categoryData?.name?.toUpperCase() || props.categoryBadge;

  function validate_inventory(product) {
    return product && inventory.includes(product.id)
  }

  return (
    <li key={product.id}>
      <div
        className="product-card"
        onClick={(event) => {
          if (
            event.target.id !== 'addToCart' &&
            event.target.parentNode.id !== 'addToCart'
          ) {
            navigate(itemLink, { state: product });
          }
        }}
      >
        <div className="product-image-container">
          <img src={product.img} alt="product" className="sentry-block" />
          {categoryBadge && <span className="category-badge">{categoryBadge}</span>}</div>
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
