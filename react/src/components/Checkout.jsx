import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import measureRequestDuration from '../utils/measureRequestDuration';
import './checkout.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux';
import Loader from 'react-loader-spinner';
import { countItemsInCart } from '../utils/cart';
import { getTag } from '../utils/utils';


function Checkout({ backend, rageclick, checkout_success, cart }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  let initialFormValues;
  let se = sessionStorage.getItem('se');
  const seTdaPrefixRegex = /[^-]+-tda-[^-]+-/;
  if (se && seTdaPrefixRegex.test(se)) {
    // we want form actually filled out in TDA for a realistic-looking Replay
    initialFormValues = {
      email: '',
      subscribe: '',
      firstName: '',
      lastName: '',
      address: '',
      city: '',
      country: '',
      state: '',
      zipCode: '',
    };
  } else {
    initialFormValues = {
      email: 'plant.lover@example.com',
      subscribe: '',
      firstName: 'Jane',
      lastName: 'Greenthumb',
      address: '123 Main Street',
      city: 'San Francisco',
      country: 'United States of America',
      state: 'CA',
      zipCode: '94122',
    };
  }
  const [form, setForm] = useState(initialFormValues);

async function checkout(cart, checkout_span) {
    console.log("Checkout called with cart:", cart);
    console.log("Checkout span:", checkout_span);
    const itemsInCart = countItemsInCart(cart);
    console.log("Calculated itemsInCart:", itemsInCart);
    
    if (!checkout_span || typeof checkout_span.setAttribute !== 'function') {
        console.error("Invalid checkout_span object:", checkout_span);
        return;
    }
    
    checkout_span.setAttribute("checkout.click", 1);
    checkout_span.setAttribute("items_at_checkout", itemsInCart);
    
    let tags = { 'backendType': getTag('backendType'), 'cexp': getTag('cexp'), 'items_at_checkout': itemsInCart, 'checkout.click': 1 };
    checkout_span.setAttributes(tags);
    const stopMeasurement = measureRequestDuration('/checkout');
    const response = await fetch(backend + '/checkout?v2=true', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cart: cart,
        form: form,
        validate_inventory: checkout_success ? "false" : "true",
      }),
    })
    .catch((err) => {
      checkout_span.setAttributes({
        "checkout.error": 1,
        "status": 500
      })
      return { ok: false, status: 500 };
    })
    .then((res) => {
      stopMeasurement();
      return res;
    });
    if (!response.ok) {
      checkout_span.setAttributes({
        "checkout.error": 1,
        "status": response.status
      })

      throw new Error(
        [response.status, response.statusText || ' Internal Server Error'].join(
          ' -'
        )
      );
    }
    checkout_span.setAttribute("checkout.success", 1)
    checkout_span.setAttribute("checkout.order.total", cart.total);

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

    if (rageclick) {
      // do nothing. after enough clicks,
      // Sentry will detect a rageclick
      return;
    }

    Sentry.startSpan({
      name: 'Submit Checkout Form',
      forceTransaction: true,
    }, async (span) => {
      let hadError = false;

      window.scrollTo({
        top: 0,
        behavior: 'auto',
      });

      setLoading(true);

      try {
        await checkout(cart, span);
      } catch (error) {
        Sentry.captureException(error);
        hadError = true;
      }
      setLoading(false);

      if (hadError) {
        navigate('/error');
      } else {
        navigate('/complete');
      }
    })
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
