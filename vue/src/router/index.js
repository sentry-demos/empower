import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/ProductsView.vue";
import ManualView from '../views/ManualView.vue'
import AboutView from "../views/AboutView.vue"
import SubscribeView from '../views/SubscribeView.vue'
import ErrorView from '../views/ErrorView.vue'
import HomePage from "../components/HomePage.vue";
import ProductsView from "../views/ProductsView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomePage,
    },
    {
      path: "/products",
      name: "products",
      component: ProductsView,
    },
    {
      path: "/about",
      name: "about",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      // component: () => import("../views/AboutView.vue"),
      component: AboutView,
    },
    {
      path: "/subscribe",
      name: "subscribe",
      component: SubscribeView,
    },
    {
      path: "/error",
      name: "error",
      component: ErrorView,
    },
    {
      path: "/trigger",
      name: "trigger",
      component: ManualView,
    },
  ],
});

export default router;
