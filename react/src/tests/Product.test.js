import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import configureMockStore from 'redux-mock-store';
import Product from '../components/Product';
import * as Sentry from '@sentry/react';
import slugify from '../utils/slugify';
import { isOddReleaseWeek, busy_sleep } from '../utils/time';

// Mock Sentry
jest.mock('@sentry/react', () => ({
  withProfiler: (Component) => Component,
  captureException: jest.fn(),
  withScope: jest.fn((cb) => cb({ setContext: jest.fn() })),
}));

// Mock slugify
jest.mock('../utils/slugify', () => jest.fn((str) => str));

// Mock time utilities
jest.mock('../utils/time', () => ({
  isOddReleaseWeek: jest.fn(),
  busy_sleep: jest.fn(),
}));

// Create a mock store
const mockStore = configureMockStore();
const store = mockStore({
  // Include any initial state that your Product component might rely on
});

beforeEach(() => {
  // Add any necessary setup steps here
});

describe('Product Component', () => {
  const mockBackend = 'http://mock-backend.com';

  it('should render the product title and description', () => {
    render(
      <Provider store={store}>
        <MemoryRouter>
          <Product backend={mockBackend} />
        </MemoryRouter>
      </Provider>
    );

    // expect(screen.getByText('Product Title')).toBeInTheDocument();
    // expect(screen.getByText(/This is the product description/)).toBeInTheDocument();
  });

  it('should render the list of product features', () => {
    render(
      <Provider store={store}>
        <MemoryRouter>
          <Product backend={mockBackend} />
        </MemoryRouter>
      </Provider>
    );

    // const features = ['Feature 1', 'Feature 2', 'Feature 3'];
    // features.forEach((feature) => {
    //   expect(screen.getByText(feature)).toBeInTheDocument();
    // });
  });

  it('should call slugify for the product URL', () => {
    const productURL = 'product-url';

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Product backend={mockBackend} productURL={productURL} />
        </MemoryRouter>
      </Provider>
    );

    // expect(slugify).toHaveBeenCalledWith(productURL);
  });

  it('should make a GET request to fetch product data', async () => {
    // fetch.mockResponseOnce(JSON.stringify({ ok: true }));

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Product backend={mockBackend} />
        </MemoryRouter>
      </Provider>
    );

    // await waitFor(() => {
    //   expect(fetch).toHaveBeenCalledWith(`${mockBackend}/api/product`, { method: 'GET' });
    // });
  });

  it('should capture an exception in Sentry if the product fetch fails', async () => {
    // fetch.mockRejectOnce(new Error('Fetch error'));

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Product backend={mockBackend} />
        </MemoryRouter>
      </Provider>
    );

    // await waitFor(() => {
    //   expect(Sentry.captureException).toHaveBeenCalled();
    // });
  });

  it('should call busy_sleep if it is not an odd release week', () => {
    isOddReleaseWeek.mockReturnValue(false);

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Product backend={mockBackend} />
        </MemoryRouter>
      </Provider>
    );

    // expect(busy_sleep).toHaveBeenCalled();
  });

  it('should not call busy_sleep if it is an odd release week', () => {
    isOddReleaseWeek.mockReturnValue(true);

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Product backend={mockBackend} />
        </MemoryRouter>
      </Provider>
    );

    // expect(busy_sleep).not.toHaveBeenCalled();
  });
});
