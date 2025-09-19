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

      <nav class="nav">
        <RouterLink to="/about">About</RouterLink>
        <RouterLink to="/products">Products</RouterLink>
        <RouterLink to="/checkout">Cart</RouterLink>
        <RouterLink to="/subscribe">Subscribe</RouterLink>
      </nav>
    </header>
  <RouterView />
</div>
</template>

<script>
import logo from "@/assets/empowerplant-logo.svg"; 

export default {
  data(){
    return {
      logo,
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
  line-height: 1.5;
  max-height: 100vh;
}

.nav-logo {
  display: flex;
  font-size: 1.8rem;
  padding: 1rem;
  padding-left: 70px;
  color: black;
  text-decoration: none;
  width: -webkit-fill-available
}

.logo {
  display: block;
  max-height: 3rem;
}



nav {
  width: 100%;
  font-size: 20px;
  text-align: center;
  margin-top: 2rem;
}

nav a {
  color: black;
  text-decoration: none;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

</style>
