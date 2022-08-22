import { Component } from 'react';
import Context from '../utils/context';
import { Link } from 'react-router-dom';
import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux'
import { setProducts, addProduct, setFlag } from '../actions'

class ProductCard extends Component {
  static contextType = Context;

  // componentDidMount updates props so that the ui.react.update Span will appear in the transaction
  async componentDidMount(){
    this.props.setFlag()
  }

  render() {

    const product = this.props.product
    const itemLink = '/product/' + product.id
    const stars = this.props.stars

    return (
        <li key={product.id}>
            <div>
            <Link to={itemLink}>
                <img src={product.img} alt="product" />
                <div>
                <h2>{product.title}</h2>
                <p className="product-description">
                    {product.description}
                </p>
                </div>
            </Link>
            <button
                onClick={() => this.props.addProduct(product)}
            >
                Add to cart — ${product.price}.00
            </button>
            <p>{stars} ({product.reviews.length})</p>
            </div>
        </li>
    )
  }
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
  