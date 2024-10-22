import * as Sentry from '@sentry/react';
import plantsBackground from '../../public/plants-background-img.jpg';
import Button from '../components/ButtonLink';
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import {
  determineBackendType,
  determineBackendUrl,
} from '../utils/backendrouter';

const divStyle = {
  backgroundImage: 'url(' + plantsBackground.src + ')',
};

function Home() {
  const { query } = useRouter();
  const { backend } = query;
  const backendType = determineBackendType(backend);
  const backendUrl = determineBackendUrl(backendType);

  useEffect(() => {
    try {
      // This should be the only http request for home page, for health check purposes
      fetch(backendUrl + '/success', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    } catch (err) {
      Sentry.captureException(err);
    }
  }, []);

  return (
    <div className="hero sentry-unmask">
      <div className="hero-bg-img" style={divStyle}></div>
      <div className="hero-content">
        <h1>Empower your plants</h1>
        <p>Keep your houseplants happy.</p>
        <Button to={'/products'} params={query}>
          Browse products
        </Button>
      </div>
    </div>
  );
}
export default Home;
