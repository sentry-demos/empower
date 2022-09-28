import { defineStore } from "pinia";

export const useCounterStore = defineStore({
  id: "counter",
  state: () => ({
    counter: 0,
    cart: [],
  }),
  actions: {
    updatePrice(val = 1) {
      this.counter += val;
    },
    updateCart(product) {
      this.cart.push(product);
      console.log("cart", this.cart);
      // if (this.cart.length() > 0) {
      //   this.cart.forEach((eachCartItem) => {
      //     if (eachCartItem.id === product.id) {
      //       return;
      //     } else {
      //       this.cart.push(product);
      //     }
      //   });
      // } else {
      //   this.cart.push(product);
      // }
    },
  },
});
