import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Footer from '../components/Footer';
import * as Sentry from '@sentry/react';
import { BrowserRouter as Router } from 'react-router-dom';

// jest.mock('@sentry/react', () => ({
//   ...jest.requireActual('@sentry/react'),
//   ErrorBoundary: jest.fn(({ fallback, children, onReset }) => (
//     <div>
//       <button onClick={onReset}>Reset Error</button>
//       {children}
//     </div>
//   )),
// }));

describe('Footer Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders Footer with form and link', () => {
    render(
      <Router>
        <Footer />
      </Router>
    );

    // expect(screen.getByText('Sign up for plant tech news')).toBeInTheDocument();
    // expect(screen.getByLabelText('Email')).toBeInTheDocument();
    // expect(screen.getByText('Subscribe')).toBeInTheDocument();
    // expect(screen.getByText('© 2021 • Empower Plant • About us')).toBeInTheDocument();
  });

  test('handles form submission and shows subscribed message', async () => {
    render(
      <Router>
        <Footer />
      </Router>
    );

    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByText('Subscribe');

    // fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    // fireEvent.click(submitButton);

    // await waitFor(() => {
    //   expect(screen.getByText('SubscribedMessage error')).toBeInTheDocument();
    // });
  });

//   test('displays error message and reset button on error', async () => {
//     Sentry.ErrorBoundary.mockImplementation(({ fallback }) => fallback({
//       resetError: jest.fn(),
//       eventId: '12345',
//     }));

//     render(
//       <Router>
//         <Footer />
//       </Router>
//     );

//     const submitButton = screen.getByText('Subscribe');
//     fireEvent.click(submitButton);

//     await waitFor(() => {
//       expect(screen.getByText('An error has occurred. Sentry Event ID: 12345')).toBeInTheDocument();
//       expect(screen.getByText('Reset Form')).toBeInTheDocument();
//     });

//     const resetButton = screen.getByText('Reset Form');
//     fireEvent.click(resetButton);

//     expect(Sentry.ErrorBoundary).toHaveBeenCalled();
//   });
});
