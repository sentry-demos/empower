<template>
  <div class="checkout">
    <div class="cart-container">
    <h1>Checkout</h1>
    <hr />
    <div 
      class="cart-item" 
      v-for="(item, index) in cartItems" 
      :key="item.id"
    >
      <img class="item-image" :src="item.imgcropped" :alt="`Image for item ${item.id}`" />
      <div class="item-details">
        <p class="item-title">Item {{ item.id }}</p>
        <p class="item-price">${{ item.price.toFixed(2) }}</p>
        <div class="item-quantity">
          <button @click="decreaseQuantity(item)">-</button>
          <span>{{ item.count }}</span>
          <button @click="increaseQuantity(item)">+</button>
        </div>
        <p class="item-total">${{ item.totalPrice.toFixed(2) }}</p>
      </div>
    </div>
    <hr />
  </div>
    <form @submit.prevent="handleSubmit" class="checkout-form">
      <h1>Contact Form</h1>
      <div class="section">
        <label for="email">Email</label>
        <input type="email" id="email" v-model="email" required />
      </div>

      <div class="section">
        <h2>Shipping address</h2>
        <label for="firstName">First Name</label>
        <input type="text" id="firstName" v-model="firstName" required />

        <label for="lastName">Last Name</label>
        <input type="text" id="lastName" v-model="lastName" required />

        <label for="address">Address</label>
        <input type="text" id="address" v-model="address" required />

        <label for="city">City</label>
        <input type="text" id="city" v-model="city" required />

        <label for="country">Country/Region</label>
        <select id="country" v-model="country" required>
          <option value="United States of America">United States of America</option>
          <!-- Add more countries as needed -->
        </select>

        <label for="state">State</label>
        <input type="text" id="state" v-model="state" required />

        <label for="zipCode">Zip Code</label>
        <input type="text" id="zipCode" v-model="zipCode" required />
      </div>

      <button type="submit" class="submit-button">Submit</button>
      <a href="/products" class="back-link">Back to products</a>
    </form>
  </div>
</template>
    
<script>
import * as Sentry from "@sentry/vue";
import { useCounterStore } from "../stores/cart";

  export default {
  data() {
    return {
      store: useCounterStore(),
      email: 'plant.lover@example.com',
      subscribe: false,
      firstName: 'Jane',
      lastName: 'Greenthumb',
      address: '123 Main Street',
      city: 'San Francisco',
      country: 'United States of America',
      state: 'CA',
      zipCode: '94122'
    };
  },
  computed: {
    // Access the store's properties and methods through computed properties
    cartItems() {
      return this.store.getCartItems();
    },
    cartTotal() {
      return this.store.getTotalPrice(); // example if you have a cart total in the store
    },
    cartQuantities(){
      return this.store.getQuantities()
    },
    contactForm(){
      return {
        email,
        firstName,
        lastName,
        address,
        city,
        country,
        state,
        zipCode
      }
    }
  },
  methods: {
    decreaseQuantity: (item) => {
      const store = useCounterStore();
      store.decreaseQuantity(item);
    },
    increaseQuantity: (item) => {
      const store = useCounterStore();
      store.increaseQuantity(item)
    },
    makeCheckoutRequest: function(requestOptions) {
      const backendUrl = window.BACKEND_URL + '/checkout';
      Sentry.logger.debug(`Making checkout request to endpoint: ${backendUrl}`)
      return fetch(
          backendUrl,
          requestOptions
        ).then(function (response) {
          if (!response.ok) {
            const err = new Error(
              response.status +
                " -- " +
                (response.statusText || "Internal Server Error")
            );
            Sentry.logger.error(`Checkout request failed with status: ${response.status}`)
            throw err
            
          } else {
            Sentry.logger.trace(`Checkout request successful`)
            return true;
          }
        });
    },

    handleSubmit() {
      let success = null;

      Sentry.startNewTrace(() => {
        Sentry.startSpan({ name: "Checkout" }, async (span) => {
          const payload = {
            cart: {
              items: this.cartItems,
              quantities: this.cartQuantities,
              total: this.cartTotal,
            },
            form: this.contactForm,          
          }
          var requestOptions = {
            method: "POST",
            headers: {
              "Content-Type": "text/plain",
            },
            body: JSON.stringify(payload),
            redirect: "follow",
          };

          try {
            success = await this.makeCheckoutRequest(requestOptions);
          } catch (error) {
            Sentry.withActiveSpan(span, async () => {
              Sentry.captureException(error);
            })
            this.$router.push("/error");

          }

          return success;
        })
      })

      if (!success) {
        this.$router.push("/error");
      }
    }
  }
};
</script>

  <style scoped>
  .checkout {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
    color: #333;
    margin-bottom: 8rem;
  }

  h1 {
    text-align: center;
  }

  .checkout-form {
    display: flex;
    flex-direction: column;
    margin-top: 2em;
  }

  .section {
    margin-bottom: 20px;
    margin-top: 2rem;
  }

  h2 {
    font-size: 1.2em;
    margin-bottom: 10px;
  }

  label {
    font-weight: bold;
    margin-top: 10px;
  }

  input,
  select {
    width: 100%;
    padding: 8px;
    margin-top: 5px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  .checkbox {
    align-items: center;
    margin-top: 10px;
  }

  .checkbox input {
    margin-right: 10px;
  }

  .submit-button {
    width: 100%;
    padding: 10px;
    background-color: #333;
    color: #fff;
    border: none;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
    margin-top: 20px;
  }

  .submit-button:hover {
    background-color: #555;
  }

  .back-link {
    display: block;
    text-align: center;
    margin-top: 10px;
    color: #333;
    text-decoration: none;
  }

  .back-link:hover {
    text-decoration: underline;
  }

  .cart-container {
  font-family: Arial, sans-serif;
  text-align: center;
  color: #2f2f2f;
  padding: 20px;
}

h1 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.cart-item {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  margin-top: 1.5rem;
}

.item-image {
  width: 100px;
  height: auto;
  margin-right: 1rem;
}

.item-details {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.item-title {
  font-size: 1.2rem;
  font-weight: bold;
}

.item-price,
.item-total {
  font-size: 1rem;
}

.item-quantity {
  display: flex;
  align-items: center;
}

.item-quantity button {
  width: 30px;
  height: 30px;
  font-size: 1rem;
  cursor: pointer;
  background-color: #2f2f2f;
  color: white;
  border: none;
  margin: 0px 0.5rem 0 0.5rem;
}

.cart-summary {
  margin-top: 2rem;
}
  </style>