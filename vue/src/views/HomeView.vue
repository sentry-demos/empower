<script>
import ProductSummary from "../components/ProductSummary.vue";
import * as Sentry from "@sentry/vue";
import {useCounterStore} from '../stores/counter'

export default {
  name: "app",
  components: {
    ProductSummary
  },
  data: function() {
    return { 
      products: [],
      loading: true,
      disabledStatus: false,
      checkoutCartPrice: 0
    };
  },

  methods: {
    checkout: function() {
      this.disabledStatus = true
      const transaction = Sentry.startTransaction({ name: "checkout-cart" });
      // Do this or the trace won't include the backend transaction
      Sentry.getCurrentHub().configureScope(scope => scope.setSpan(transaction));

      console.log("checkout...");
      console.log(transaction)
      const traceAndSpanID = transaction.traceId + "-" + transaction.spanId;

      var raw = "{\"cart\":{\"items\":[{\"id\":4,\"title\":\"Botana Voice\",\"description\":\"Lets plants speak for themselves.\",\"descriptionfull\":\"Now we don't want him to get lonely, so we'll give him a little friend. Let your imagination just wonder around when you're doing these things. Let your imagination be your guide. Nature is so fantastic, enjoy it. Let it make you happy.\",\"price\":175,\"img\":\"https://storage.googleapis.com/application-monitoring/plant-to-text.jpg\",\"imgcropped\":\"https://storage.googleapis.com/application-monitoring/plant-to-text-cropped.jpg\",\"pg_sleep\":\"\",\"reviews\":[{\"id\":4,\"productid\":4,\"rating\":4,\"customerid\":null,\"description\":null,\"created\":\"2021-06-04 00:12:33.553939\",\"pg_sleep\":\"\"},{\"id\":5,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-06-04 00:12:45.558259\",\"pg_sleep\":\"\"},{\"id\":6,\"productid\":4,\"rating\":2,\"customerid\":null,\"description\":null,\"created\":\"2021-06-04 00:12:50.510322\",\"pg_sleep\":\"\"},{\"id\":13,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:12:43.312186\",\"pg_sleep\":\"\"},{\"id\":14,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:12:54.719873\",\"pg_sleep\":\"\"},{\"id\":15,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:12:57.760686\",\"pg_sleep\":\"\"},{\"id\":16,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:13:00.140407\",\"pg_sleep\":\"\"},{\"id\":17,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:13:00.971730\",\"pg_sleep\":\"\"},{\"id\":18,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:13:01.665798\",\"pg_sleep\":\"\"},{\"id\":19,\"productid\":4,\"rating\":3,\"customerid\":null,\"description\":null,\"created\":\"2021-07-01 00:13:02.278934\",\"pg_sleep\":\"\"}]}],\"quantities\":{\"4\":2},\"total\":350},\"form\":{\"loading\":false}}";
      
      var requestOptions = {
        method: 'POST',
        headers: {"Content-Type": "text/plain", "sentry-trace": traceAndSpanID},
        body: raw,
        redirect: 'follow'
      };

      fetch("https://application-monitoring-flask-dot-sales-engineering-sf.appspot.com/checkout", requestOptions)
        .then(function(response) {
          if (!response.ok) {
            const err = new Error(response.status + " -- " + (response.statusText || "Internal Server Error"));
            Sentry.captureException(err);
            console.error(err);
          }
          console.log("transaction.finish");
          transaction.finish(); 
          // introduces an unhandled error
          transactionComplete = true;
        });   

        // The delay has been added to complete the transaction
        setTimeout(() => {
          this.$router.push('/error');
        }, 1000)
    },

    addToCartPrice: function() {
      const store = useCounterStore()
      this.checkoutCartPrice = store.counter;
      // console.log('price', this.checkoutCartPrice)
      // console.log(store.counter)
    }
  },

  mounted() {
    try {
    // Do this or the trace won't include the backend transaction
    const transaction = Sentry.getCurrentHub().getScope().getTransaction();
    let span = {};
    if (transaction) {
      span = transaction.startChild({
        op: "http_request",
        description: "load_products",
    })}
    console.log('transaction', transaction)
    console.log('traceid', transaction.traceId)
    console.log('spanID', transaction.spanId)
    const traceAndSpanID = transaction.traceId + "-" + transaction.spanId;

    console.log("getProducts...");
      var requestOptions = {
        method: 'GET',
        headers: {"Content-Type": "application/json", "sentry-trace": traceAndSpanID},
        redirect: 'follow'
      };

      fetch("https://application-monitoring-flask-dot-sales-engineering-sf.appspot.com/products", requestOptions)
        .then(response => response.text())
        .then(result => {
          this.products = JSON.parse(result); 
          this.loading = false;
          span.finish();
          transaction.finish();
          // Generating Undefined error
          transactionComplete = true;
          })
        .catch(error => {
          console.log('error', error);
        });
      console.log(span)
    
    } catch (ex) {
      console.log(ex);
    } 
    // finally {
    // span.finish();
    // transaction.finish();
    // }
  },
}

</script>

<template>
  <div class="loading-container">
    <div v-if="loading" class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
  </div>
  <div class="home">
    <!-- <button @click="store.increment()">Increment</button>
    <h3>Count: {{store.counter}}</h3> -->
    <div id="app">
      <div id="product-list">
        <div :onClick="addToCartPrice">
          <!-- <ProductSummary :products="products" :onClick="addToCartPrice"/> -->
          <ProductSummary :products="products"/>
        </div>
      </div>
      <div class="button-container">
        <button v-if="!loading" class="checkout-button" :onClick="checkout" :disabled='disabledStatus'>Checkout your cart ($ {{checkoutCartPrice}})</button>
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
  }

  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
}

  .checkout-button {
    font-family: 'Poppins', sans-serif;
  }

  .checkout-button,
  a.btn,
  input[type='submit'] {
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
  input[type='submit']:hover {
    cursor: pointer;
    background-color: #f6cfb2;
    color: #002626;
  }
  .checkout-button:active,
  a.btn:active,
  input[type='submit']:active {
    background-color: grey;
  }
}
</style>