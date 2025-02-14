import { Link } from 'react-router-dom';
import slugify from '../utils/slugify';
import * as Sentry from '@sentry/react';
import './about.css';
import { isOddReleaseWeek, busy_sleep } from '../utils/time';
import { useEffect } from 'react';

import Jane from './employees/jane';
import Lily from './employees/lily';
import Keith from './employees/keith';
import Mason from './employees/mason';
import Emma from './employees/emma';
import Noah from './employees/noah';

const employees = [Jane, Lily, Keith, Mason, Emma, Noah];


function About({ backend }) {
  useEffect(() => {
    const fetchData = async () => {
      if (!isOddReleaseWeek()) {
        busy_sleep(Math.random(25) + 100);
      }

      try {
        // Create requests in parallel
        const requests = [
          fetch(backend + '/api'),
          fetch(backend + '/organization'),
          fetch(backend + '/connect')
        ];

        // Wait for all requests to complete
        const responses = await Promise.allSettled(requests);

        // Process each response
        responses.forEach((result) => {
          if (result.status === 'rejected') {
            // Handle network errors
            Sentry.withScope((scope) => {
              scope.setContext('error', { message: result.reason.message });
              Sentry.captureException(result.reason);
            });
          } else if (!result.value.ok) {
            // Handle HTTP error responses
            Sentry.withScope((scope) => {
              scope.setContext('response', {
                status: result.value.status,
                statusText: result.value.statusText,
                url: result.value.url
              });
              Sentry.captureException(
                new Error(
                  `${result.value.status} - ${result.value.statusText || 'Server Error'}`
                )
              );
            });
          }
        });
      } catch (error) {
        // Handle any unexpected errors
        Sentry.captureException(error);
      }
    };

    fetchData();
  }, [backend]); // Add backend to dependency array

  return (
    <div className="about-page">
      <div>
        <div className="about-info">
          <h1>About us</h1>
          <p>
            Empower Plant is an IoT company determined to keep house plants
            happy. After reading Michael Pollan's 2013 New Yorker article ("The
            Intelligent Plant"), the wife-and-wife founding team invested their
            life savings in measuring and improving the emotional state of their
            leafy housemates. Seven years later, the company's grown from its
            humble roots in the couples' backyard greenhouse (converted from a
            garage) into a Series C-funded San Francisco startup and the world's
            most accurate plant mood measurer ("a must-have for any responsible
            plant parent," according to Plant Parenthood Magazine). Their
            original state-of-the-art product is a technological marvel built
            with a plant-first mindset, and they now offer a range of
            plant-centric options.
          </p>
          <p>
            Today, the company employs 170 people (and 852 plants) in San
            Francisco, New York City, Denver, and Kiev.
          </p>
        </div>
      </div>
      <div>
        <ul className="employee-list">
          {employees.map((employee) => {
            return (
              <li key={employee.name}>
                <Link to={`/employee/${slugify(employee.url)}`}>
                  <img src={employee.img} alt={`${employee.name}`} />
                  <h5 className="employee-name" name={employee.name}>
                    {employee.name}
                  </h5>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}

export default Sentry.withProfiler(About, { name: 'About' });
