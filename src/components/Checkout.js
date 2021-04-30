import { Component } from 'react';
import { createBrowserHistory } from 'history';
import { Link } from 'react-router-dom';
import './checkout.css';

const history = createBrowserHistory();

class Checkout extends Component {
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

  handleSubmit(event) {
    console.log('Form Submitted', this.state);
    history.push('/error');
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
            id="yes"
            name="yes"
            type="checkbox"
            onChange={handleInputChange}
            defaultValue={this.state.yes}
          />
          <label htmlFor="yes">
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

export default Checkout;
