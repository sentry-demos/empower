import { useEffect } from 'react';

function Nplusone({ backend }) {
  const idRequests = 20;

  useEffect(() => {
    const ids = Array.from({ length: idRequests }, (_, i) => i);
    fetch(backend + '/product/0/info/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids }),
    });
  }, []);

  return (
    <div>
      <h1>API N+1 Performance Issue</h1>
      executed GET product id's {idRequests} times
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
