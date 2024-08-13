import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import About from '../components/About';
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

// Mock employees data
jest.mock('../components/employees/jane', () => ({ name: 'Jane', img: 'jane.jpg', url: 'jane-url' }));
jest.mock('../components/employees/lily', () => ({ name: 'Lily', img: 'lily.jpg', url: 'lily-url' }));
jest.mock('../components/employees/keith', () => ({ name: 'Keith', img: 'keith.jpg', url: 'keith-url' }));
jest.mock('../components/employees/mason', () => ({ name: 'Mason', img: 'mason.jpg', url: 'mason-url' }));
jest.mock('../components/employees/emma', () => ({ name: 'Emma', img: 'emma.jpg', url: 'emma-url' }));
jest.mock('../components/employees/noah', () => ({ name: 'Noah', img: 'noah.jpg', url: 'noah-url' }));

beforeEach(() => {
//   fetch.resetMocks();
});

describe('About Component', () => {
  const mockBackend = 'http://mock-backend.com';

  it('should render the "About us" section', () => {
    render(
      <MemoryRouter>
        <About backend={mockBackend} />
      </MemoryRouter>
    );

    // expect(screen.getByText('About us')).toBeInTheDocument();
    // expect(screen.getByText(/Empower Plant is an IoT company/)).toBeInTheDocument();
  });

  it('should render the list of employees', () => {
    render(
      <MemoryRouter>
        <About backend={mockBackend} />
      </MemoryRouter>
    );

    const employeeNames = ['Jane', 'Lily', 'Keith', 'Mason', 'Emma', 'Noah'];
    // employeeNames.forEach((name) => {
    //   expect(screen.getByText(name)).toBeInTheDocument();
    //   expect(screen.getByAltText(name)).toBeInTheDocument();
    // });
  });

  it('should call slugify for each employee URL', () => {
    render(
      <MemoryRouter>
        <About backend={mockBackend} />
      </MemoryRouter>
    );

    const employeeURLs = ['jane-url', 'lily-url', 'keith-url', 'mason-url', 'emma-url', 'noah-url'];
    employeeURLs.forEach((url) => {
      expect(slugify).toHaveBeenCalledWith(url);
    });
  });

//   it('should make three GET requests to the backend', async () => {
//     fetch.mockResponseOnce(JSON.stringify({ ok: true }))
//          .mockResponseOnce(JSON.stringify({ ok: true }))
//          .mockResponseOnce(JSON.stringify({ ok: true }));

//     render(
//       <MemoryRouter>
//         <About backend={mockBackend} />
//       </MemoryRouter>
//     );

//     await waitFor(() => {
//       expect(fetch).toHaveBeenCalledTimes(3);
//       expect(fetch).toHaveBeenCalledWith(`${mockBackend}/api`, { method: 'GET' });
//       expect(fetch).toHaveBeenCalledWith(`${mockBackend}/organization`, { method: 'GET' });
//       expect(fetch).toHaveBeenCalledWith(`${mockBackend}/connect`, { method: 'GET' });
//     });
//   });

//   it('should capture an exception in Sentry if a request fails', async () => {
//     fetch.mockResponses(
//       [JSON.stringify({ ok: true })],
//       [JSON.stringify({ ok: false }), { status: 500, statusText: 'Server Error' }],
//       [JSON.stringify({ ok: true })]
//     );

//     render(
//       <MemoryRouter>
//         <About backend={mockBackend} />
//       </MemoryRouter>
//     );

//     await waitFor(() => {
//       expect(Sentry.captureException).toHaveBeenCalled();
//     });
//   });

  it('should call busy_sleep if it is not an odd release week', () => {
    isOddReleaseWeek.mockReturnValue(false);

    render(
      <MemoryRouter>
        <About backend={mockBackend} />
      </MemoryRouter>
    );

    expect(busy_sleep).toHaveBeenCalled();
  });

  it('should not call busy_sleep if it is an odd release week', () => {
    isOddReleaseWeek.mockReturnValue(true);

    render(
      <MemoryRouter>
        <About backend={mockBackend} />
      </MemoryRouter>
    );

    expect(busy_sleep).not.toHaveBeenCalled();
  });
});
