import { useNavigate } from 'react-router-dom';
import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import { setProducts, addProduct, setFlag } from '../actions';

function ProductCard(props) {
  const navigate = useNavigate();
  const product = props.product;
  const itemLink = '/product/' + product.id;
  const stars = props.stars;
  const inventory = props.inventory || {};
  const inventoryCount = inventory[product.id] || 0;
  const isOutOfStock = inventoryCount === 0;
  const isLowStock = inventoryCount > 0 && inventoryCount <= 3;

  function validate_inventory(product) {
    // Check if the product has inventory available
    const count = inventory[product.id] || 0;
    return count > 0;
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
        <img
          src={product.img}
          alt="product"
          className="sentry-block"
          elementtiming="product-card-image"
        />
        <div>
          <h2>{product.title}</h2>
          <p className="product-description">{product.description}</p>
          {isOutOfStock && (
            <p style={{ color: 'red', fontWeight: 'bold' }}>Out of Stock</p>
          )}
          {isLowStock && (
            <p style={{ color: 'orange', fontWeight: 'bold' }}>
              Only {inventoryCount} left in stock!
            </p>
          )}
        </div>
        <button
          id="addToCart"
          onClick={() => {
            if (validate_inventory(product)) {
              props.addProduct(product);
              Sentry.metrics.count('cart.add', 1, {
                attributes: { source: 'products_list', product_id: product.id },
              });
            } else {
              Sentry.captureMessage(`Attempted to add out-of-stock product: ${product.title}`);
            }
          }}
          disabled={isOutOfStock}
          style={{
            backgroundColor: isOutOfStock ? '#ccc' : undefined,
            cursor: isOutOfStock ? 'not-allowed' : 'pointer',
          }}
        >
          {isOutOfStock ? (
            <span className="sentry-unmask">Out of Stock</span>
          ) : (
            <>
              <span className="sentry-unmask">Add to cart — $</span>
              {product.price}.00
            </>
          )}
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
    inventory: state.inventory,
  };
};

export default connect(mapStateToProps, { setProducts, addProduct, setFlag })(
  Sentry.withProfiler(ProductCard, { name: 'ProductCard' })
);
