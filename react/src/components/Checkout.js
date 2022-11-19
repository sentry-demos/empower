import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './checkout.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux'
import Loader from "react-loader-spinner";

function Checkout(props) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ 
    email: '',
    subscribe: '',
    firstName: '',
    lastName: '',
    address: '',
    city: '',
    country: '',
    state: '',
    zipCode: ''
  });

  async function checkout(cart) {
    let se, customerType, email
    Sentry.withScope(function(scope) {
      [ se, customerType ] = [scope._tags.se, scope._tags.customerType ]
      email = scope._user.email
    });

    return await fetch(props.backend + "/checkout", {
      method: "POST",
      headers: { se, customerType, email, "Content-Type": "application/json" },
      body: JSON.stringify({
        cart: cart,
        form: form
      })
    })
    .catch((err) => { 
      return { ok: false, status: 500 }
    })
  }

  function handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;
    setForm({ ...form, [name]: value })    
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const {cart} = props;

    const transaction = Sentry.startTransaction({ name: "Submit Checkout Form" });
    // Do this or the trace won't include the backend transaction
    Sentry.configureScope(scope => scope.setSpan(transaction));

    window.scrollTo({
      top: 0, 
      behavior: 'auto'
    });

    setLoading(true)

    let response = await checkout(cart)
    if (!response.ok) {
      Sentry.captureException(new Error(response.status + " - " + (response.statusText || "Internal Server Error") + ""))
    }

    setLoading(false)
    transaction.finish();

    if (!response.ok) {
      navigate('/error')
    } else {
      navigate('/complete')
    }
  }

  return (
    <div className="checkout-container">
      {loading ? (
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
          defaultValue={form.email}
          placeholder="joebobson@joeb.com"
        />

        <input
          id="subscribe"
          name="subscribe"
          type="checkbox"
          onChange={handleInputChange}
          defaultValue={form.subscribe}
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
          defaultValue={form.firstName}
          placeholder="Joe"
          className="half-width"
        />
        <label htmlFor="lastName">Last Name</label>
        <input
          id="lastName"
          name="lastName"
          type="text"
          onChange={handleInputChange}
          defaultValue={form.lastName}
          placeholder="Bobson"
        />

        <label htmlFor="address">Address</label>
        <input
          id="address"
          name="address"
          type="text"
          onChange={handleInputChange}
          defaultValue={form.address}
          placeholder="123 Main Street"
        />

        <label htmlFor="city">City</label>
        <input
          id="city"
          name="city"
          type="text"
          onChange={handleInputChange}
          defaultValue={form.city}
          placeholder="Hope Springs"
        />

        <label htmlFor="country">Country/Region</label>
        <input
          id="country"
          name="country"
          type="text"
          onChange={handleInputChange}
          defaultValue={form.country}
          placeholder="United States of America"
        />

        <label htmlFor="state">State</label>
        <input
          id="state"
          name="state"
          type="text"
          onChange={handleInputChange}
          defaultValue={form.state}
          placeholder="Indiana"
        />

        <label htmlFor="zipCode">Zip Code</label>
        <input
          id="zipCode"
          name="zipCode"
          type="text"
          onChange={handleInputChange}
          defaultValue={form.zipCode}
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

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products
  }
}

export default connect(
  mapStateToProps,
  {}
)(Sentry.withProfiler(Checkout, { name: "Checkout"}))