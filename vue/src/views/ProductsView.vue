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
    makeCheckoutRequest: function(requestOptions) {
      return fetch(
          "http://localhost:8088/checkout",
          requestOptions
        ).then(function (response) {
          if (!response.ok) {
            const err = new Error(
              response.status +
                " -- " +
                (response.statusText || "Internal Server Error")
            );
            Sentry.captureException(err);
            return false;
          } else {
            return true;
          }
        });
    },
    checkout: function () {
      this.disabledStatus = true;
      let internalTagSE = this.SE;
      let success = null;

      Sentry.startSpan({ name: "Checkout", forceTransaction: true}, async () => {
        var raw =
        '{"cart":{"items":[{"id":4,"title":"Botana Voice","description":"Lets plants speak for themselves.","descriptionfull":"Now we don\'t want him to get lonely, so we\'ll give him a little friend. Let your imagination just wonder around when you\'re doing these things. Let your imagination be your guide. Nature is so fantastic, enjoy it. Let it make you happy.","price":175,"img":"https://storage.googleapis.com/application-monitoring/plant-to-text.jpg","imgcropped":"https://storage.googleapis.com/application-monitoring/plant-to-text-cropped.jpg","pg_sleep":"","reviews":[{"id":4,"productid":4,"rating":4,"customerid":null,"description":null,"created":"2021-06-04 00:12:33.553939","pg_sleep":""},{"id":5,"productid":4,"rating":3,"customerid":null,"description":null,"created":"2021-06-04 00:12:45.558259","pg_sleep":""},{"id":6,"productid":4,"rating":2,"customerid":null,"description":null,"created":"2021-06-04 00:12:50.510322","pg_sleep":""},{"id":13,"productid":4,"rating":3,"customerid":null,"description":null,"created":"2021-07-01 00:12:43.312186","pg_sleep":""},{"id":14,"productid":4,"rating":3,"customerid":null,"description":null,"created":"2021-07-01 00:12:54.719873","pg_sleep":""},{"id":15,"productid":4,"rating":3,"customerid":null,"description":null,"created":"2021-07-01 00:12:57.760686","pg_sleep":""},{"id":16,"productid":4,"rating":3,"customerid":null,"description":null,"created":"2021-07-01 00:13:00.140407","pg_sleep":""},{"id":17,"productid":4,"rating":3,"customerid":null,"description":null,"created":"2021-07-01 00:13:00.971730","pg_sleep":""},{"id":18,"productid":4,"rating":3,"customerid":null,"description":null,"created":"2021-07-01 00:13:01.665798","pg_sleep":""},{"id":19,"productid":4,"rating":3,"customerid":null,"description":null,"created":"2021-07-01 00:13:02.278934","pg_sleep":""}]}],"quantities":{"4":2},"total":350},"form":{"loading":false}}';
        var requestOptions = {
          method: "POST",
          headers: {
            "Content-Type": "text/plain",
          },
          body: raw,
          redirect: "follow",
        };

        success = await this.makeCheckoutRequest(requestOptions);
        return success;
      })

      if (!success) {
        this.$router.push("/error");
      }
    },

    addToCartPrice: function () {
      const store = useCounterStore();
      this.checkoutCartPrice = store.counter;
      this.checkoutCart = store.cart;
    },
  },

  mounted() {
    try {
      fetch(
        "http://localhost:8088/products"
      )
        .then((response) => response.text())
        .then((result) => {
          this.products = JSON.parse(result);
          this.loading = false;
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
            Checkout your cart ($ {{ checkoutCartPrice }})
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
