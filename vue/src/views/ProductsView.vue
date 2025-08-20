<script>
import ProductSummary from "../components/ProductSummary.vue";
import * as Sentry from "@sentry/vue";
import { useCounterStore } from "../stores/cart";

export default {
  name: "app",
  components: {
    ProductSummary,
  },
  data: function () {
    return {
      products: [],
      loading: true,
      disabledStatus: false,
      checkoutCartPrice: 0,
      checkoutCart: [],
      SE: "",
    };
  },

  methods: {
    checkout: function () {
      this.$router.push("/checkout");
    },

    addToCartPrice: function () {
      const store = useCounterStore();
      this.checkoutCartPrice = store.counter;
      this.checkoutCart = store.cart;
    },
  },

  mounted() {
    const backendUrl = window.BACKEND_URL + '/products';
    Sentry.logger.trace(`Fetching products from endpoint: ${backendUrl}`)
    try {
      fetch(
        backendUrl
      )
        .then((response) => response.text())
        .then((result) => {
          this.products = JSON.parse(result);
          this.loading = false;
          Sentry.logger.trace(`Products fetched successfully, found ${this.products.length} products`)
        })
        .catch((error) => {
          console.log("error", error);
        });
    } catch (ex) {
      console.log(ex);
    }

    if ("se" in this.$route.query) {
      this.SE = this.$route.query.se;
      console.log(this.SE);
    }
  },
};
</script>

<template>
  <div>
    <div class="loading-container">
      <div v-if="loading" class="lds-ellipsis">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    </div>
    <div class="home">
      <!-- <button @click="store.increment()">Increment</button>
    <h3>Count: {{store.counter}}</h3> -->
      <div id="app">
        <div class="button-container">
          <button
            v-if="!loading"
            class="checkout-button"
            :onClick="checkout"
            :disabled="disabledStatus"
          >
            Checkout ($ {{ checkoutCartPrice }})
          </button>
        </div>
        <div id="product-list">
          <div :onClick="addToCartPrice">
            <!-- <ProductSummary :products="products" :onClick="addToCartPrice"/> -->
            <ProductSummary :products="products" />
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style>
@media (min-width: 1px) {
  .home {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
  .lds-ellipsis {
    display: inline-block;
    position: relative;
    width: 80px;
    height: 80px;
  }
  .lds-ellipsis div {
    position: absolute;
    top: 33px;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: #dfc;
    animation-timing-function: cubic-bezier(0, 1, 1, 0);
  }
  .lds-ellipsis div:nth-child(1) {
    left: 8px;
    animation: lds-ellipsis1 0.6s infinite;
  }
  .lds-ellipsis div:nth-child(2) {
    left: 8px;
    animation: lds-ellipsis2 0.6s infinite;
  }
  .lds-ellipsis div:nth-child(3) {
    left: 32px;
    animation: lds-ellipsis2 0.6s infinite;
  }
  .lds-ellipsis div:nth-child(4) {
    left: 56px;
    animation: lds-ellipsis3 0.6s infinite;
  }
  @keyframes lds-ellipsis1 {
    0% {
      transform: scale(0);
    }
    100% {
      transform: scale(1);
    }
  }
  @keyframes lds-ellipsis3 {
    0% {
      transform: scale(1);
    }
    100% {
      transform: scale(0);
    }
  }
  @keyframes lds-ellipsis2 {
    0% {
      transform: translate(0, 0);
    }
    100% {
      transform: translate(24px, 0);
    }
  }

  .button-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 50px;
  }

  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .checkout-button {
    font-family: "Poppins", sans-serif;
  }

  .checkout-button,
  a.btn,
  input[type="submit"] {
    -webkit-appearance: none;
    background-color: #dddc4e;
    color: #002626;
    padding: 0.75rem 1rem;
    line-height: 1.5;
    border-radius: 0.25em;
    border: none;
    text-decoration: none;
    font-size: 1rem;
    margin: 0.5rem 0;
  }

  .checkout-button:hover,
  a.btn:hover,
  input[type="submit"]:hover {
    cursor: pointer;
    background-color: #f6cfb2;
    color: #002626;
  }
  .checkout-button:active,
  a.btn:active,
  input[type="submit"]:active {
    background-color: grey;
  }
}
</style>
