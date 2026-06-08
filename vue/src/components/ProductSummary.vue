<template>
  <ul class="products-list">
    <li v-for="product in products" :key="product.id">
      <div class="product-card">
        <div class="product-image-wrap">
          <img :src="product.img" :alt="product.title" />
        </div>
        <div class="product-info">
          <h2 class="product-title">{{ product.title }}</h2>
          <p class="product-description">{{ product.description }}</p>
        </div>
        <button @click="addToCartPrice(product)" class="add-to-cart-btn">
          Add to cart — ${{ product.price }}.00
        </button>
      </div>
    </li>
  </ul>
</template>

<script>
import { useCounterStore } from "../stores/cart";

export default {
  props: {
    products: Array,
  },
  methods: {
    addToCartPrice(product) {
      const store = useCounterStore();
      store.updateCart(product);
      store.updatePrice(product.price);
    },
  },
};
</script>

<style scoped>
.products-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.product-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.product-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.product-image-wrap {
  background: #f9fafb;
  aspect-ratio: 4 / 3;
  overflow: hidden;
}

.product-image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  padding: 1rem 1.25rem 0.5rem;
  flex: 1;
}

.product-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111;
  margin-bottom: 0.35rem;
}

.product-description {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
}

.add-to-cart-btn {
  margin: 0.75rem 1.25rem 1.25rem;
  padding: 0.6rem 1rem;
  background: #111;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.add-to-cart-btn:hover {
  background: #333;
}

.add-to-cart-btn:active {
  background: #000;
}
</style>
