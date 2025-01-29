import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import Products from '../components/Products';
import * as Sentry from '@sentry/react';
import measureRequestDuration from '../utils/measureRequestDuration';

jest.mock('../utils/measureRequestDuration');
jest.mock('react-loader-spinner', () => () => <div>Loader</div>);
jest.mock('@sentry/react', () => ({
  withScope: jest.fn((fn) => fn({ _tags: { se: 'mocked_se' } })),
  captureException: jest.fn(),
  setContext: jest.fn(),
  startSpan: jest.fn(),
  withProfiler: (Component) => Component,
}));

jest.mock('../components/ProductCard', () => ({ product, stars }) => (
  <div data-testid="product-card">
    <h2>{product.title}</h2>
    <p>{product.description}</p>
    <p>{stars} ({product.reviews.length})</p>
  </div>
));

describe('Products Component', () => {
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
    measureRequestDuration.mockReturnValue(jest.fn());
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders loader initially', () => {
    render(
      <Provider store={store}>
        <Products frontendSlowdown={false} backend="http://backend" />
      </Provider>
    );

    // expect(screen.getByText('Loader')).toBeInTheDocument();
  });

  test('fetches and renders products', async () => {
    render(
      <Provider store={store}>
        <Products frontendSlowdown={false} backend="http://backend" />
      </Provider>
    );

    // await waitFor(() => expect(fetch).toHaveBeenCalledTimes(4)); // 3 background endpoints + 1 products endpoint

    // expect(screen.getByText('Product 1')).toBeInTheDocument();
    // expect(screen.getByText('Description 1')).toBeInTheDocument();
    // expect(screen.getByText('Product 2')).toBeInTheDocument();
    // expect(screen.getByText('Description 2')).toBeInTheDocument();
    // expect(screen.getAllByTestId('product-card')).toHaveLength(2);
  });

  test('fetches uncompressed assets when frontendSlowdown is true', async () => {
    render(
      <Provider store={store}>
        <Products frontendSlowdown={true} backend="http://backend" />
      </Provider>
    );

    // await waitFor(() => expect(fetch).toHaveBeenCalledTimes(4)); // 3 background endpoints + 1 products endpoint

    // expect(document.querySelector('script[src*="compressed_small_file.js"]')).toBeInTheDocument();
    // expect(document.querySelector('script[src*="uncompressed_big_file.js"]')).toBeInTheDocument();
  });

  test('captures exception when fetching fails', async () => {
    global.fetch.mockImplementationOnce(() => Promise.reject('Fetch failed'));

    render(
      <Provider store={store}>
        <Products frontendSlowdown={false} backend="http://backend" />
      </Provider>
    );

    await waitFor(() => expect(Sentry.captureException).toHaveBeenCalledTimes(1));
  });
});
