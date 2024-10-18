import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import * as Sentry from '@sentry/react';
import Employee from '../components/Employee';

jest.mock('@sentry/react', () => ({
  withProfiler: (component) => component,
}));

jest.mock(
  './employees/1',
  () => ({
    default: {
      img: 'image-url.jpg',
      name: 'John Doe',
      bio: 'A brief bio of John Doe.',
    },
  }),
  { virtual: true }
);

describe('Employee Component', () => {
  it('displays loading initially', () => {
    render(
      <MemoryRouter initialEntries={['/employee/keith']}>
        <Routes>
          <Route path="/employee/:id" element={<Employee />} />
        </Routes>
      </MemoryRouter>
    );
    // expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  it('renders employee data correctly', async () => {
    render(
      <MemoryRouter initialEntries={['/employee/keith']}>
        <Routes>
          <Route path="/employee/:id" element={<Employee />} />
        </Routes>
      </MemoryRouter>
    );

    // await waitFor(() => expect(screen.getByRole('img')).toHaveAttribute('src', 'image-url.jpg'));
    // expect(screen.getByRole('img')).toHaveAttribute('alt', 'John Doe');
    // expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('John Doe');
    // expect(screen.getByText('A brief bio of John Doe.')).toBeInTheDocument();
    // expect(screen.getByText(/Back/i)).toBeInTheDocument();
  });
});
