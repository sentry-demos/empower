<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
<div>
  <header class="header">
    <a class="nav-logo" href="/">
      <img :src="logo" alt="Empower Plant Logo" class="logo" />
      Empower Plant
    </a>
    <div class="show-desktop">
      <nav class="nav" id="top-right-links">
        <RouterLink to="/about">About</RouterLink>
        <RouterLink to="/products">Products</RouterLink>
        <RouterLink to="/cart" class="cart-link">
          Cart
          <span v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</span>
        </RouterLink>
        <RouterLink to="/subscribe">Subscribe</RouterLink>
      </nav>
    </div>
  </header>
  <RouterView />
</div>
</template>

<script>
import logo from "@/assets/empowerplant-logo.svg";
import { useCounterStore } from "@/stores/cart";

export default {
  data(){
    return {
      logo,
    }
  },
  computed: {
    cartCount() {
      return useCounterStore().cart.reduce((sum, item) => sum + item.count, 0);
    }
  }
}
</script>

<style>
@import "@/assets/base.css";

#app {
  font-weight: normal;
}

header {
  display: flex;
  align-items: center;
  padding: 0 2rem;
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #111;
  text-decoration: none;
  white-space: nowrap;
}

.logo {
  display: block;
  height: 2rem;
}

.show-desktop {
  margin-left: auto;
}

nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
}

nav a {
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.75rem;
  color: #555;
  font-size: 0.95rem;
  text-decoration: none;
  border-radius: 6px;
  border: none;
  transition: background 0.15s, color 0.15s;
}

nav a:hover {
  background: #f3f4f6;
  color: #111;
}

nav a.router-link-exact-active {
  color: #111;
  font-weight: 500;
}

.cart-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #111;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 999px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  margin-left: 5px;
}
</style>
