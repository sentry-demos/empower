import {
    ADD_PRODUCT,
    REMOVE_PRODUCT,
    RESET_CART,
    SET_PRODUCTS,
    SET_FLAG,
  } from '../actions/types';
  import { addProduct, resetCart, setProducts, removeProduct, setFlag } from '../actions/index';
  
  describe('Action Creators', () => {
    it('should create an action to add a product', () => {
      const product = { id: 1, name: 'Product 1' };
      const expectedAction = {
        type: ADD_PRODUCT,
        payload: {
          product,
        },
      };
      expect(addProduct(product)).toEqual(expectedAction);
    });
  
    it('should create an action to reset the cart', () => {
      const expectedAction = {
        type: RESET_CART,
        payload: {},
      };
      expect(resetCart()).toEqual(expectedAction);
    });
  
    it('should create an action to set products', () => {
      const products = [
        { id: 1, name: 'Product 1' },
        { id: 2, name: 'Product 2' },
      ];
      const expectedAction = {
        type: SET_PRODUCTS,
        payload: {
          products,
        },
      };
      expect(setProducts(products)).toEqual(expectedAction);
    });
  
    it('should create an action to remove a product', () => {
      const product = { id: 1, name: 'Product 1' };
      const expectedAction = {
        type: REMOVE_PRODUCT,
        payload: {
          product,
        },
      };
      expect(removeProduct(product)).toEqual(expectedAction);
    });
  
    it('should create an action to set a flag', () => {
      const expectedAction = {
        type: SET_FLAG,
        payload: {},
      };
      expect(setFlag()).toEqual(expectedAction);
    });
  });
  