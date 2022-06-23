import { Component } from 'react';
import Context from '../utils/context';
import { Link } from 'react-router-dom';
import './checkout.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux'
import { setProducts, addProduct } from '../actions'
import Loader from "react-loader-spinner";

class Checkout extends Component {
  static contextType = Context;

  constructor() {
    super();
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
    this.state = {
      loading: false
    };
  }

  async shouldComponentUpdate() {
    console.log("> Checkout shouldComponentUpdate")
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    this.setState({
      ...this.state,
      [name]: value,
    });
  }

  async checkout(cart) {
    let se, customerType, email
    Sentry.withScope(function(scope) {
      [ se, customerType ] = [scope._tags.se, scope._tags.customerType ]
      email = scope._user.email
    });

    console.log("checking out =>>>>>>>>> " + this.props.backend)
    return await fetch(this.props.backend + "/checkout", {
      method: "POST",
      headers: { se, customerType, email, "Content-Type": "application/json" },
      body: JSON.stringify({
        cart: cart,
        form: this.state
      })
    })
    .catch((err) => { 
      return { ok: false, status: 500 }
    })
  }

  async handleSubmit(event) {
    event.preventDefault();

    const {cart} = this.props;
    console.log('Form Submitted - state', this.state);
    console.log('Form Submitted - Cart', cart);

    const transaction = Sentry.startTransaction({ name: "Submit Checkout Form" });
    // Do this or the trace won't include the backend transaction
    Sentry.configureScope(scope => scope.setSpan(transaction));

    window.scrollTo({
      top: 0, 
      behavior: 'auto'
    });

    this.setState({...this.state,loading: true});

    let response = await this.checkout(cart)
    if (!response.ok) {
      Sentry.captureException(new Error(response.status + " - " + (response.statusText || "Internal Server Error")))
    }

    this.setState({...this.state,loading: false});
    transaction.finish();

    if (!response.ok) {
      this.props.history.push('/error', {"error": "errorInfo"})
    } else {
      this.props.history.push('/complete', {"complete": "completeOrderInfo"})
    }
  }

  render() {
    const { handleSubmit, handleInputChange } = this;
    return (
      <div className="checkout-container">
        {this.state.loading ? (
        <Loader
        type="ThreeDots"
        color="#f6cfb2"
        height={150}
        width={150}
        />) : (
        <>
        <h2>Checkout</h2>
        <form className="checkout-form" onSubmit={handleSubmit}>
          <h4>Contact information</h4>

          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            onChange={handleInputChange}
            defaultValue={this.state.email}
            placeholder="joebobson@joeb.com"
          />

          <input
            id="subscribe"
            name="subscribe"
            type="checkbox"
            onChange={handleInputChange}
            defaultValue={this.state.subscribe}
          />
          <label htmlFor="subscribe">
            Keep me updated with new sales and products
          </label>

          <h4>Shipping address</h4>
          <label htmlFor="firstName">First Name</label>
          <input
            id="firstName"
            name="firstName"
            type="text"
            onChange={handleInputChange}
            defaultValue={this.state.firstName}
            placeholder="Joe"
            className="half-width"
          />
          <label htmlFor="lastName">Last Name</label>
          <input
            id="lastName"
            name="lastName"
            type="text"
            onChange={handleInputChange}
            defaultValue={this.state.lastName}
            placeholder="Bobson"
          />

          <label htmlFor="address">Address</label>
          <input
            id="address"
            name="address"
            type="text"
            onChange={handleInputChange}
            defaultValue={this.state.address}
            placeholder="123 Main Street"
          />

          <label htmlFor="city">City</label>
          <input
            id="city"
            name="city"
            type="text"
            onChange={handleInputChange}
            defaultValue={this.state.city}
            placeholder="Hope Springs"
          />

          <label htmlFor="country">Country/Region</label>
          <input
            id="country"
            name="country"
            type="text"
            onChange={handleInputChange}
            defaultValue={this.state.country}
            placeholder="United States of America"
          />

          <label htmlFor="state">State</label>
          <input
            id="state"
            name="state"
            type="text"
            onChange={handleInputChange}
            defaultValue={this.state.state}
            placeholder="Indiana"
          />

          <label htmlFor="zipCode">Zip Code</label>
          <input
            id="zipCode"
            name="zipCode"
            type="text"
            onChange={handleInputChange}
            defaultValue={this.state.zipCode}
            placeholder="45678"
          />

          <input
            type="submit"
            className="complete-checkout-btn"
            defaultValue="Complete order"
          />
        </form>
        <Link to="/cart">Back to cart</Link>
        </>
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
  { setProducts, addProduct }
)(Sentry.withProfiler(Checkout, { name: "Checkout"}))