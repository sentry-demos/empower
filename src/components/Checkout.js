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

    let response = await fetch(`${BACKEND}/checkout`, {
      method: "POST",
      // headers: {
      //   "Access-Control-Allow-Origin": "*",
      //   // "Access-Control-Allow-Headers": "Content-Type, Authorization",
      //   // "Content-Type": "application/json"
      //   // "Content-Type": "application/x-www-form-urlencoded"
      // },
      body: JSON.stringify({
        cart: cart,
        form: this.state
      })
    })
      // .then(response => { return response }) // if you do response.text() then .ok .status aren't available later
      .catch((err) => { 
        console.log("> catches error", err)
        throw Error(err) 
      })

    console.log("> response", response)
    console.log("> ok | status | statusText", response.ok, response.status, response.statusText)
    // console.log("> /checkout status", response.status)

    // TODO if error then go to /error page, if no error then go to /complete page
    this.props.history.push('/error', { state: {"example": "error"}})
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