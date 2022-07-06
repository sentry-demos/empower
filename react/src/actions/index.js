import { 
    ADD_PRODUCT,
    REMOVE_PRODUCT,
    RESET_CART,
    SET_PRODUCTS,
    SET_FLAG 
  } from './types'
  
  export const addProduct = product => ({
    type: ADD_PRODUCT,
    payload: {
      product
    }
  })
  export const resetCart = () => ({
    type: RESET_CART,
    payload: {}
  })
  export const setProducts = products => ({
    type: SET_PRODUCTS,
    payload: {
      products
    }
  })
  export const removeProduct = product => ({
    type: REMOVE_PRODUCT,
    payload: {
      product
    }
  })
  export const setFlag = () => ({
    type: SET_FLAG,
    payload: {}
  })