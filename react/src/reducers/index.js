// products: [productOne, productTwo, productThree, productFour]
const initialState = {
    cart: {
        items: [],
        quantities: {},
        total: 0
    },
    products: [],
    flag: false
}

  const newState = (cart, products, flag) => {
    return {
      cart,
      products,
      flag
    }
  }
  
  const reducer = (state = initialState, action) => {
      
      const { payload, type } = action
  
      switch (type) {
        case "ADD_PRODUCT":
          var cart = Object.assign({}, state.cart)
          let item = cart.items.find((x) => x.id === payload.product.id);
          if (!item) cart.items.push(payload.product);
          cart.quantities[payload.product.id] = cart.quantities[payload.product.id] || 0;
          cart.quantities[payload.product.id]++;
          cart.total = cart.items.reduce((a, item) => {
            const itemTotal = item.price * cart.quantities[item.id];
            return a + itemTotal;
          }, 0);
          return Object.assign({}, newState(cart, state.products))

        case "REMOVE_PRODUCT":
          var cart1 = Object.assign({}, state.cart)
          let item1 = cart1.items.find((x) => x.id === payload.product.id);
          if (!item1) Object.assign({}, newState(cart1, state.products));
          cart1.quantities[payload.product.id]--;
          if (cart1.quantities[payload.product.id] === 0) {
            delete cart1.quantities[payload.product.id];
            const i = cart1.items.findIndex((x) => x.id === payload.product.id);
            cart1.items.splice(i, 1);
          }

          cart1.total = cart1.items.reduce((a, item) => {
            const itemTotal = item.price * cart1.quantities[item.id];
            return a + itemTotal;
          }, 0);
          return Object.assign({}, newState(cart1, state.products))
  
        case "RESET_CART":
          return Object.assign({}, newState([], state.tools))
  
        case "SET_PRODUCTS":
          return Object.assign({}, newState(state.cart, payload.products))        

        case "SET_FLAG":
          // Toggles the state of the flag, which changes props in ProductCard.js and gives us the ui.react.update span
          return Object.assign({}, newState(state.cart, state.products, !state.flag))       
        
        default:
          return state;
      }
    };
  
  export default reducer