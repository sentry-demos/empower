import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router } from 'react-router-dom';
import Checkout from '../components/Checkout';
import configureStore from 'redux-mock-store';
import * as Sentry from '@sentry/react';

jest.mock('react-loader-spinner', () => () => <div data-testid="loader" />);
jest.mock('@sentry/react', () => ({
  ...jest.requireActual('@sentry/react'),
  captureException: jest.fn(),
  metrics: {
    increment: jest.fn(),
    distribution: jest.fn(),
  },
  startSpan: jest.fn((span, fn) => fn()),
}));

const mockStore = configureStore([]);

describe('Checkout Component', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      cart: { items: [], total: 100 },
      products: [],
    });
    jest.clearAllMocks();
  });

  test('renders Checkout form', () => {
    render(
      <Provider store={store}>
        <Router>
          <Checkout backend="/api" rageclick={false} />
        </Router>
      </Provider>
    );

    // expect(screen.getByText(/Checkout/i)).toBeInTheDocument();
    // expect(screen.getByPlaceholderText(/plant.lover@example.com/i)).toBeInTheDocument();
    // expect(screen.getByPlaceholderText(/123 Main Street/i)).toBeInTheDocument();
  });

  //   test('handles input change', () => {
  //     render(
  //       <Provider store={store}>
  //         <Router>
  //           <Checkout backend="/api" rageclick={false} />
  //         </Router>
  //       </Provider>
  //     );

  //     const emailInput = screen.getByPlaceholderText(/plant.lover@example.com/i);
  //     fireEvent.change(emailInput, { target: { value: 'new.email@example.com' } });

  //     expect(emailInput.value).toBe('new.email@example.com');
  //   });

  //   test('submits the form and handles navigation on success', async () => {
  //     const mockNavigate = jest.fn();
  //     const mockCheckout = jest.fn().mockResolvedValue({ ok: true });

  //     jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);
  //     jest.spyOn(require('../components/Checkout'), 'checkout').mockImplementation(mockCheckout);

  //     render(
  //       <Provider store={store}>
  //         <Router>
  //           <Checkout backend="/api" rageclick={false} />
  //         </Router>
  //       </Provider>
  //     );

  //     fireEvent.submit(screen.getByRole('button', { name: /Complete order/i }));

  //     await waitFor(() => {
  //       expect(mockCheckout).toHaveBeenCalledTimes(1);
  //       expect(mockNavigate).toHaveBeenCalledWith('/complete');
  //       expect(Sentry.metrics.increment).toHaveBeenCalledWith('checkout.success');
  //     });
  //   });

  //   test('handles checkout error and navigates to error page', async () => {
  //     const mockNavigate = jest.fn();
  //     const mockCheckout = jest.fn().mockRejectedValue(new Error('Checkout failed'));

  //     jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);
  //     jest.spyOn(require('./Checkout'), 'checkout').mockImplementation(mockCheckout);

  //     render(
  //       <Provider store={store}>
  //         <Router>
  //           <Checkout backend="/api" rageclick={false} />
  //         </Router>
  //       </Provider>
  //     );

  //     fireEvent.submit(screen.getByRole('button', { name: /Complete order/i }));

  //     await waitFor(() => {
  //       expect(mockCheckout).toHaveBeenCalledTimes(1);
  //       expect(mockNavigate).toHaveBeenCalledWith('/error');
  //       expect(Sentry.captureException).toHaveBeenCalledWith(expect.any(Error));
  //     });
  //   });
});
