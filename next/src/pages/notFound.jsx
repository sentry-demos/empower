import Link from 'next/link';

function NotFound() {
  return (
    <div className="checkout-container-complete">
      <h2>404</h2>
      <p>
        The page you're looking for can't be found and we can't get to the root
        of it just yet. Please go back in your browser or go{' '}
        <Link href="/">back to our home page</Link> and accept our deepest
        apologies.
      </p>
      <p>
        If the issue persists, please <Link href="/">contact us</Link>.
      </p>
    </div>
  );
}

export default NotFound;
// export default Sentry.withProfiler(NotFound, { name: "NotFound"})
