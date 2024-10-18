import reducer from '../reducers/index';
import {
  ADD_PRODUCT,
  REMOVE_PRODUCT,
  RESET_CART,
  SET_PRODUCTS,
  SET_FLAG,
} from '../actions/types';

describe('Reducer', () => {
  const productOne = { id: 1, name: 'Product 1', price: 10 };
  const productTwo = { id: 2, name: 'Product 2', price: 20 };
  const initialState = {
    cart: {
      items: [],
      quantities: {},
      total: 0,
    },
    products: [],
    flag: false,
  };

  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual(initialState);
  });

  it('should handle ADD_PRODUCT', () => {
    const action = {
      type: ADD_PRODUCT,
      payload: {
        product: productOne,
      },
    };
    const expectedState = {
      ...initialState,
      cart: {
        items: [productOne],
        quantities: { 1: 1 },
        total: 10,
      },
      flag: undefined,
    };
    expect(reducer(initialState, action)).toEqual(expectedState);
  });

  it('should handle REMOVE_PRODUCT', () => {
    const stateWithProduct = {
      ...initialState,
      cart: {
        items: [productOne],
        quantities: { 1: 1 },
        total: 10,
      },
    };
    const action = {
      type: REMOVE_PRODUCT,
      payload: {
        product: productOne,
      },
    };
    const expectedState = {
      ...initialState,
      cart: {
        items: [],
        quantities: {},
        total: 0,
      },
      flag: undefined,
    };
    expect(reducer(stateWithProduct, action)).toEqual(expectedState);
  });

  it('should handle RESET_CART', () => {
    const stateWithProducts = {
      ...initialState,
      cart: {
        items: [productOne, productTwo],
        quantities: { 1: 1, 2: 1 },
        total: 30,
      },
    };
    const action = {
      type: RESET_CART,
    };
    const expectedState = {
      ...initialState,
      cart: [],
      products: undefined,
      flag: undefined,
    };
    expect(reducer(stateWithProducts, action)).toEqual(expectedState);
  });

  it('should handle SET_PRODUCTS', () => {
    const action = {
      type: SET_PRODUCTS,
      payload: {
        products: [productOne, productTwo],
      },
    };
    const expectedState = {
      ...initialState,
      products: [productOne, productTwo],
      flag: undefined,
    };
    expect(reducer(initialState, action)).toEqual(expectedState);
  });

  it('should handle SET_FLAG', () => {
    const action = {
      type: SET_FLAG,
    };
    const expectedState = {
      ...initialState,
      flag: true,
    };
    expect(reducer(initialState, action)).toEqual(expectedState);
  });
});
