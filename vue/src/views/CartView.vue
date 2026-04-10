<template>
  <div class="cart">
    <h1>Cart</h1>
    <hr />
    <div
      class="cart-item"
      v-for="item in cartItems"
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
    <a href="/checkout" class="checkout-link">Proceed to Checkout</a>
  </div>
</template>

<script>
import { useCounterStore } from "../stores/cart";

export default {
  computed: {
    cartItems() {
      return useCounterStore().getCartItems();
    },
  },
  methods: {
    decreaseQuantity(item) {
      useCounterStore().decreaseQuantity(item);
    },
    increaseQuantity(item) {
      useCounterStore().increaseQuantity(item);
    },
  },
};
</script>

<style scoped>
.cart {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  color: #333;
}

h1 {
  text-align: center;
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
  margin: 0 0.5rem;
}

.checkout-link {
  display: block;
  text-align: center;
  margin-top: 1.5rem;
  padding: 10px;
  background-color: #333;
  color: #fff;
  text-decoration: none;
  border-radius: 4px;
  font-weight: bold;
}

.checkout-link:hover {
  background-color: #555;
}
</style>
