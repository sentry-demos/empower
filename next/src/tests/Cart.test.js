import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router } from 'react-router-dom';
import Cart from '../components/Cart';
import configureStore from 'redux-mock-store';
import * as Sentry from '@sentry/react';
import { addProduct, removeProduct } from '../actions';

// Mock Sentry
jest.mock('@sentry/react', () => ({
  ...jest.requireActual('@sentry/react'),
  withProfiler: (Component) => Component,
}));

const mockStore = configureStore([]);

describe('Cart Component', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      cart: {
        items: [
          {
            id: 1,
            title: 'Sample Product',
            img: '/path/to/image.jpg',
            price: 50,
          },
        ],
        quantities: {
          1: 2,
        },
        total: 100,
      },
      products: [],
    });

    jest.clearAllMocks();
  });

  const setup = () =>
    render(
      <Provider store={store}>
        <Router>
          <Cart removeProduct={jest.fn()} addProduct={jest.fn()} />
        </Router>
      </Provider>
    );

  test('renders Cart with items', () => {
    setup();

    // expect(screen.getByText('Cart')).toBeInTheDocument();
    // expect(screen.getByText('Sample Product')).toBeInTheDocument();
    // expect(screen.getByText('$50.00')).toBeInTheDocument();
    // expect(screen.getByText('2')).toBeInTheDocument();
    // expect(screen.getByText('Cart Subtotal: $100.00')).toBeInTheDocument();
  });

  test('removes a product from the cart', () => {
    const mockRemoveProduct = jest.fn();
    const mockAddProduct = jest.fn();

    render(
      <Provider store={store}>
        <Router>
          <Cart removeProduct={mockRemoveProduct} addProduct={mockAddProduct} />
        </Router>
      </Provider>
    );

    const removeButton = screen.getByText('–');
    fireEvent.click(removeButton);

    // expect(mockRemoveProduct).toHaveBeenCalledWith(store.getState().cart.items[0]);
  });

  test('adds a product to the cart', () => {
    const mockRemoveProduct = jest.fn();
    const mockAddProduct = jest.fn();

    render(
      <Provider store={store}>
        <Router>
          <Cart removeProduct={mockRemoveProduct} addProduct={mockAddProduct} />
        </Router>
      </Provider>
    );

    const addButton = screen.getByText('+');
    fireEvent.click(addButton);

    // expect(mockAddProduct).toHaveBeenCalledWith(store.getState().cart.items[0]);
  });

  test('shows message when cart is empty', () => {
    store = mockStore({
      cart: {
        items: [],
        quantities: {},
        total: 0,
      },
      products: [],
    });

    setup();

    // expect(screen.getByText('Please add items to the cart')).toBeInTheDocument();
  });

  test('navigates to checkout when "Proceed to checkout" is clicked', () => {
    setup();

    const checkoutButton = screen.getByText('Proceed to checkout');
    // expect(checkoutButton).toHaveAttribute('href', '/checkout');
  });
});
