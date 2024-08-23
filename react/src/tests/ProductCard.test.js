import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import configureStore from 'redux-mock-store';
import * as Sentry from '@sentry/react';
import { addProduct } from '../actions';

// Mock Sentry
jest.mock('@sentry/react', () => ({
  ...jest.requireActual('@sentry/react'),
  withProfiler: (Component) => Component,
}));

// Mock react-router-dom's useNavigate
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}));

const mockStore = configureStore([]);

describe('ProductCard Component', () => {
  let store;
  let mockNavigate;

  beforeEach(() => {
    store = mockStore({
      cart: { items: [] },
      products: [],
      flag: false,
    });

    mockNavigate = require('react-router-dom').useNavigate;
    mockNavigate.mockReturnValue(jest.fn()); // Return a mock function for useNavigate

    jest.clearAllMocks();
  });

  const product = {
    id: 1,
    title: 'Sample Product',
    description: 'This is a sample product description.',
    img: '/path/to/image.jpg',
    price: 100,
    reviews: ['Good', 'Very good', 'Excellent'],
  };

  const props = {
    product,
    stars: 4,
    addProduct: jest.fn(),
  };

  test('renders ProductCard with product details', () => {
    render(
      <Provider store={store}>
        <Router>
          <ProductCard {...props} />
        </Router>
      </Provider>
    );

    // expect(screen.getByText('Sample Product')).toBeInTheDocument();
    // expect(screen.getByText('This is a sample product description.')).toBeInTheDocument();
    // expect(screen.getByText(/Add to cart — \$100.00/)).toBeInTheDocument();
    // expect(screen.getByText('4 (3)')).toBeInTheDocument();
  });

  test('navigates to product details page on image click', () => {
    render(
      <Provider store={store}>
        <Router>
          <ProductCard {...props} />
        </Router>
      </Provider>
    );

    const productImage = screen.getByAltText('product');
    fireEvent.click(productImage);

    // expect(mockNavigate).toHaveBeenCalledWith('/product/1', { state: product });
  });

//   test('adds product to cart on "Add to cart" button click', () => {
//     render(
//       <Provider store={store}>
//         <Router>
//           <ProductCard {...props} />
//         </Router>
//       </Provider>
//     );

//     const addToCartButton = screen.getByText(/Add to cart — \$100.00/);
//     fireEvent.click(addToCartButton);

//     expect(props.addProduct).toHaveBeenCalledWith(product);
//   });
})
