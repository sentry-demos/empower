import { useState } from 'react';
import { Link } from 'react-router-dom';
import './checkout.css';

function Checkout() {
  const [formState, setFormState] = useState({
    firstName: '',
    yes: false,
  });

  const handleInputChange = (event) => {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    setFormState({
      ...formState,
      [name]: value,
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log('Form Submitted', formState);
  };

  return (
    <div className="checkout-container">
      <h2>Checkout</h2>
      <form className="checkout-form" onSubmit={handleSubmit}>
        <label htmlFor="first-name">First Name</label>
        <input
          id="firstName"
          name="firstName"
          type="text"
          onChange={handleInputChange}
          value={formState.firstName}
          placeholder="Bobson"
        />

        <label htmlFor="yes">Yes?</label>
        <input
          id="yes"
          name="yes"
          type="checkbox"
          onChange={handleInputChange}
          value={formState.yes}
        />

        <input
          type="submit"
          className="complete-checkout-btn"
          value="Complete order"
        />
      </form>
      <Link to="/cart">Back to cart</Link>
    </div>
  );
}

export default Checkout;
