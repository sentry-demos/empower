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
    getQuantities(){
      let quantities = {}
      for (let item in this.cart) {
        quantities[this.cart[item].id] = this.cart[item].count
      }
      return quantities;
    },
    getTotalPrice(){
      let total = 0;
      for (let item in this.cart) {
        total += this.cart[item].totalPrice
      }
      return total;
    },
    updateCart(product) {
      let index = this.cart.findIndex( item => item.id === product.id);
      if (index === -1) {
        product.count = 1
        product.totalPrice = product.price;
        this.cart.push(product);
      } else {
        this.cart[index].totalPrice += product.price;
        this.cart[index].count += 1;
      }
    },
    getCartItems() {
      return this.cart
    },
    decreaseQuantity(item){
      const index = this.cart.findIndex(cartItem => cartItem.id === item.id);
      if (index !== -1) {
        this.cart[index].count--;
        this.cart[index].totalPrice -= this.cart[index].price;
      }
    },
    increaseQuantity(item){
      const index = this.cart.findIndex(cartItem => cartItem.id === item.id);
      if (index !== -1) {
        this.cart[index].count++;
        this.cart[index].totalPrice += this.cart[index].price;
      }
    }
  },
});
