import { useEffect } from 'react';

function Nplusone({ backend }) {
  useEffect(() => {
    fetch(backend + '/products', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
  }, []);

  return (
    <div>
      <h1>API N+1 Performance Issue (Fixed)</h1>
      fetched all products in a single batched request
      <h3>
        look at the query{' '}
        <a
          href="https://demo.sentry.io/issues/?project=5808623&query=is%3Aunresolved+issue.type%3Aperformance_n_plus_one_api_calls&referrer=issue-list&statsPeriod=14d"
          rel="noreferrer"
        >
          here
        </a>
      </h3>
    </div>
  );
}

export default Nplusone;
