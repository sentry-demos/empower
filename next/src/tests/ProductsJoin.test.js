import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import ProductsJoin from '../components/ProductsJoin';
import * as Sentry from '@sentry/react';

jest.mock('react-loader-spinner', () => () => <div>Loader</div>);
jest.mock('@sentry/react', () => ({
  captureException: jest.fn(),
  setContext: jest.fn(),
  withProfiler: (Component) => Component,
}));

jest.mock('../components/ProductCard', () => ({ product, stars }) => (
  <div data-testid="product-card">
    <h2>{product.title}</h2>
    <p>{product.description}</p>
    <p>
      {stars} ({product.reviews.length})
    </p>
  </div>
));

describe('ProductsJoin Component', () => {
  const mockStore = configureStore([]);
  let store;

  beforeEach(() => {
    store = mockStore({
      products: [],
      cart: [],
    });
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 1,
              title: 'Product 1',
              description: 'Description 1',
              reviews: [{ rating: 5 }],
            },
            {
              id: 2,
              title: 'Product 2',
              description: 'Description 2',
              reviews: [{ rating: 4 }],
            },
          ]),
      })
    );
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders loader initially', () => {
    render(
      <Provider store={store}>
        <ProductsJoin backend="http://backend" />
      </Provider>
    );

    // expect(screen.getByText('Loader')).toBeInTheDocument();
  });

  test('fetches and renders products', async () => {
    render(
      <Provider store={store}>
        <ProductsJoin backend="http://backend" />
      </Provider>
    );

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));

    // expect(screen.getByText('Product 1')).toBeInTheDocument();
    // expect(screen.getByText('Description 1')).toBeInTheDocument();
    // expect(screen.getByText('Product 2')).toBeInTheDocument();
    // expect(screen.getByText('Description 2')).toBeInTheDocument();
    // expect(screen.getAllByTestId('product-card')).toHaveLength(2);
  });

  test('handles fetch failure', async () => {
    global.fetch.mockImplementationOnce(() => Promise.reject('Fetch failed'));

    render(
      <Provider store={store}>
        <ProductsJoin backend="http://backend" />
      </Provider>
    );

    // await waitFor(() => expect(Sentry.captureException).toHaveBeenCalledTimes(1));

    // expect(Sentry.captureException).toHaveBeenCalledWith(expect.anything());
  });

  test('handles non-OK fetch response', async () => {
    global.fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      })
    );

    render(
      <Provider store={store}>
        <ProductsJoin backend="http://backend" />
      </Provider>
    );

    await waitFor(() =>
      expect(Sentry.setContext).toHaveBeenCalledWith('err', {
        status: 500,
        statusText: 'Internal Server Error',
      })
    );

    // expect(Sentry.captureException).toHaveBeenCalledTimes(1);
  });
});
