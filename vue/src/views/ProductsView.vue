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
      SE: "",
    };
  },

  mounted() {
    const backendUrl = window.BACKEND_URL + '/' + window.PRODUCTS_API;
    Sentry.logger.trace(`Fetching products from endpoint: ${backendUrl}`)
    try {
      fetch(backendUrl)
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
    }
  },
};
</script>

<template>
  <div class="products-page">
    <div class="loading-container" v-if="loading">
      <div class="lds-ellipsis">
        <div></div><div></div><div></div><div></div>
      </div>
    </div>
    <div v-else>
      <h1 class="page-title">Products</h1>
      <ProductSummary :products="products" />
    </div>
  </div>
</template>

<style>
.products-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 600;
  color: #111;
  margin-bottom: 2rem;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
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
  background: #002626;
  animation-timing-function: cubic-bezier(0, 1, 1, 0);
}
.lds-ellipsis div:nth-child(1) { left: 8px; animation: lds-ellipsis1 0.6s infinite; }
.lds-ellipsis div:nth-child(2) { left: 8px; animation: lds-ellipsis2 0.6s infinite; }
.lds-ellipsis div:nth-child(3) { left: 32px; animation: lds-ellipsis2 0.6s infinite; }
.lds-ellipsis div:nth-child(4) { left: 56px; animation: lds-ellipsis3 0.6s infinite; }

@keyframes lds-ellipsis1 { 0% { transform: scale(0); } 100% { transform: scale(1); } }
@keyframes lds-ellipsis3 { 0% { transform: scale(1); } 100% { transform: scale(0); } }
@keyframes lds-ellipsis2 { 0% { transform: translate(0, 0); } 100% { transform: translate(24px, 0); } }
</style>
