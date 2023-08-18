import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './checkout.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import Loader from 'react-loader-spinner';

function Checkout(props) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    email: 'plant.lover@gardening.com',
    subscribe: '',
    firstName: 'Jane',
    lastName: 'Greenthumb',
    address: '1199 9th Ave',
    city: 'San Francisco',
    country: 'United States of America',
    state: 'CA',
    zipCode: '94122',
  });

  async function checkout(cart) {
    let se, customerType, email;
    Sentry.withScope(function (scope) {
      [se, customerType] = [scope._tags.se, scope._tags.customerType];
      email = scope._user.email;
    });

    const response = await fetch(props.backend + '/checkout?v2=true', {
      method: 'POST',
      headers: { se, customerType, email, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cart: cart,
        form: form,
      }),
    }).catch((err) => {
      return { ok: false, status: 500 };
    });
    if (!response.ok) {
      throw new Error(
        [response.status, response.statusText || 'Internal Server Error'].join(
          ' - '
        )
      );
    }
    return response;
  }
  function generateUrl(product_id) {
    return product_id;
  }

  function handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;
    setForm({ ...form, [name]: value });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const { cart } = props;

    const transaction = Sentry.startTransaction({
      name: 'Submit Checkout Form',
    });
    // Do this or the trace won't include the backend transaction
    Sentry.configureScope((scope) => scope.setSpan(transaction));

    window.scrollTo({
      top: 0,
      behavior: 'auto',
    });

    setLoading(true);

    let hadError = false;
    try {
      await checkout(cart);
    } catch (error) {
      Sentry.captureException(error);
      hadError = true;
    }
    setLoading(false);
    transaction.finish();

    if (hadError) {
      navigate('/error');
    } else {
      navigate('/complete');
    }
  }

  return (
    <div className="checkout-container">
      {loading ? (
        <Loader
          type="ThreeDots"
          color="#f6cfb2"
          className="sentry-unmask"
          height={150}
          width={150}
        />
      ) : (
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
          <Link to="/cart" className="sentry-unmask">
            Back to cart
          </Link>
        </>
      )}
    </div>
  );
}

const mapStateToProps = (state, ownProps) => {
  return {
    cart: state.cart,
    products: state.products,
  };
};

export default connect(
  mapStateToProps,
  {}
)(Sentry.withProfiler(Checkout, { name: 'Checkout' }));
