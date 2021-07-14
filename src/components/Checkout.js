import { Component } from 'react';
import { createBrowserHistory } from 'history';
import Context from '../utils/context';
import { Link } from 'react-router-dom';
// import { useHistory } from "react-router-dom";
import './checkout.css';
import * as Sentry from '@sentry/react';
// const history = createBrowserHistory();
var BACKEND = ""
if (window.location.hostname === "localhost") {
  BACKEND = "http://localhost:8080"
} else {
  BACKEND = process.env.REACT_APP_BACKEND
}

class Checkout extends Component {
  static contextType = Context;

  constructor() {
    super();
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
    this.state = {};
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

  async handleSubmit(event) {
    event.preventDefault();

    const { cart } = this.context;
    console.log('Form Submitted - state', this.state);
    console.log('Form Submitted - Cart', cart);

    const transaction = Sentry.startTransaction({ name: "checkout" });
    // Do this or the trace won't include the backend transaction
    Sentry.configureScope(scope => scope.setSpan(transaction));

    let response = await fetch(`${BACKEND}/checkout`, {
      method: "POST",
      headers: {
        "se": "will"
        // "email": this.state.email // email here is already in the body
      },
      body: JSON.stringify({
        cart: cart,
        form: this.state
      })
    })
    .catch((err) => { 
      console.log("> catches error", err)
      throw Error(err) 
    })

    console.log("> response", response)
    console.log("> ok | status | statusText", response.ok, response.status, response.statusText)

    if (!response.ok) {
      Sentry.captureException(new Error(response.status + " - " + (response.statusText || "Internal Server Error")))
    }
    
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
      </div>
    );
  }
}

export default Sentry.withProfiler(Checkout, { name: "Checkout"})