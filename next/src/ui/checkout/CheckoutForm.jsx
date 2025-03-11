'use client'

import React, { useState } from 'react';
import * as Sentry from '@sentry/nextjs';
import { connect } from 'react-redux';
import { ThreeDots } from 'react-loader-spinner';
import ThreeDotLoader from '../ThreeDotLoader';


export function CheckoutForm({ cart, checkoutAction }) {
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    email: 'plant.lover@example.com',
    subscribe: '',
    firstName: 'Jane',
    lastName: 'Greenthumb',
    address: '123 Main Street',
    city: 'San Francisco',
    country: 'United States of America',
    state: 'CA',
    zipCode: '94122',
  });

  function handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;
    setForm({ ...form, [name]: value });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);

        window.scrollTo({
          top: 0,
          behavior: 'auto',
        });

        Sentry.metrics.increment('checkout.click');
        console.log("> cart", cart);
        // Server Action within a client component
        // Reference: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations
        await checkoutAction(cart);


      }


  return (
    <>
    {
      loading ? (
        <ThreeDotLoader
      /> ) : (
        <>
          <h2 className="sentry-unmask">Checkout</h2>
          <form className="checkout-form" onSubmit={handleSubmit}>
            <h4 className="sentry-unmask">Contact information</h4>

            <label htmlFor="email" className="sentry-unmask">
              Email
            </label>
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
            <label htmlFor="subscribe" className="sentry-unmask">
              Keep me updated with new sales and products
            </label>

            <h4 className="sentry-unmask">Shipping address</h4>
            <label htmlFor="firstName" className="sentry-unmask">
              First Name
            </label>
            <input
              id="firstName"
              name="firstName"
              type="text"
              onChange={handleInputChange}
              defaultValue={form.firstName}
              placeholder="Joe"
              className="half-width"
            />
            <label htmlFor="lastName" className="sentry-unmask">
              Last Name
            </label>
            <input
              id="lastName"
              name="lastName"
              type="text"
              onChange={handleInputChange}
              defaultValue={form.lastName}
              placeholder="Bobson"
            />

            <label htmlFor="address" className="sentry-unmask">
              Address
            </label>
            <input
              id="address"
              name="address"
              type="text"
              onChange={handleInputChange}
              defaultValue={form.address}
              placeholder="123 Main Street"
            />

            <label htmlFor="city" className="sentry-unmask">
              City
            </label>
            <input
              id="city"
              name="city"
              type="text"
              onChange={handleInputChange}
              defaultValue={form.city}
              placeholder="Hope Springs"
            />

            <label htmlFor="country" className="sentry-unmask">
              Country/Region
            </label>
            <input
              id="country"
              name="country"
              type="text"
              onChange={handleInputChange}
              defaultValue={form.country}
              placeholder="United States of America"
            />

            <label htmlFor="state" className="sentry-unmask">
              State
            </label>
            <input
              id="state"
              name="state"
              type="text"
              onChange={handleInputChange}
              defaultValue={form.state}
              placeholder="Indiana"
            />

            <label htmlFor="zipCode" className="sentry-unmask">
              Zip Code
            </label>
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
              className="complete-checkout-btn sentry-unmask"
              defaultValue="Complete order"
            />
          </form>
        </>
    )}
    </>
  )
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products,
  };
};

export default connect(mapStateToProps, {})(CheckoutForm);
