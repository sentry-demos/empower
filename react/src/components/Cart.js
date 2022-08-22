import { Component } from 'react';
import Context from '../utils/context';
import { Link } from 'react-router-dom';
import './cart.css';
import * as Sentry from '@sentry/react';
import Button from './ButtonLink';
import { connect } from 'react-redux'
import { setProducts, addProduct, removeProduct } from '../actions'

class Cart extends Component {
  static contextType = Context;

  async shouldComponentUpdate() {
    console.log("> Cart shouldComponentUpdate")
  }

  render() {
    const { cart } = this.props;

    return (
      <div className="cart-container">
        <h2>Cart</h2>
        {cart.items.length > 0 ? (
          <>
            <ul className="cart-list">
              {cart.items.map((item) => {
                const quantity = cart.quantities[item.id];
                const itemLink = '/product/' + item.id;
                return (
                  <li className="cart-item" key={item.id}>
                    <Link to={itemLink}>
                      <img src={item.img} alt="item-thumbnail" />
                    </Link>
                    <Link to={itemLink}>
                      <h4>{item.title}</h4>
                    </Link>
                    <p>${item.price}.00</p>
                    <div className="quantity-adjust">
                      <button
                        onClick={() =>
                          this.props.removeProduct(item)
                        }
                      >
                        –
                      </button>
                      <span>{quantity}</span>
                      <button
                        onClick={() =>
                          this.props.addProduct(item)
                        }
                      >
                        +
                      </button>
                    </div>
                    <p>${item.price * quantity}.00</p>
                  </li>
                );
              })}
            </ul>
            <h3 className="cart-subtotal">Cart Subtotal: ${cart.total}.00</h3>
            <Button to="/checkout">Proceed to checkout</Button>
          </>
        ) : (
          <p>Please add items to the cart</p>
        )}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products
  }
}

export default connect(
  mapStateToProps,
  { setProducts, addProduct, removeProduct }
)(Sentry.withProfiler(Cart, { name: "Cart"}))
