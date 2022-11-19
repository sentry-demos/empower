import { useNavigate } from 'react-router-dom';
import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux'
import { setProducts, addProduct, setFlag } from '../actions'

function ProductCard (props) {
  const navigate = useNavigate();
  const product = props.product
  const itemLink = '/product/' + product.id
  const stars = props.stars

  return (
    <li key={product.id}>
        <div onClick={(event) => { 
          if (event.target.id !== "addToCart") {
            navigate(itemLink, { state: product })
          }} 
        }>
            <img src={product.img} alt="product" />
            <div>
            <h2>{product.title}</h2>
            <p className="product-description">
                {product.description}
            </p>
            </div>
        <button id="addToCart" onClick={() => props.addProduct(product) }>
            Add to cart — ${product.price}.00
        </button>
        <p>{stars} ({product.reviews.length})</p>
        </div>
    </li>
  )
}

const mapStateToProps = (state, ownProps) => {
    return {
      cart: state.cart,
      products: state.products,
      flag: state.flag
    }
  }
  
export default connect(
    mapStateToProps,
    { setProducts, addProduct, setFlag }
)(Sentry.withProfiler(ProductCard, { name: "ProductCard"}))
  