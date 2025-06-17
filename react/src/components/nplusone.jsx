import { useEffect } from 'react';

function Nplusone({ backend }) {
  const idRequests = 20;

  useEffect(() => {
    // Collect all product IDs to fetch
    const productIds = Array.from({ length: idRequests }, (_, i) => i);
    const idsQueryParam = productIds.join(',');
    const batchApiUrl = `${backend}/products/batch-info?ids=${idsQueryParam}`;

    // Make a single batch request instead of multiple individual requests
    fetch(batchApiUrl, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    })
    .then(response => response.json())
    .then(data => {
      console.log('Batch product data:', data);
    })
    .catch(error => {
      console.error('Error fetching batch product data:', error);
    });
  }, [backend]);

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
