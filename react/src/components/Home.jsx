import * as Sentry from '@sentry/react';
import plantsBackground from '../assets/plants-background-img.jpg';
import Button from './ButtonLink';
import { useEffect } from 'react';
import './home.css';

const divStyle = {
  backgroundImage: 'url(' + plantsBackground + ')',
};

function Home({ frontendSlowdown, backend }) {
  useEffect(() => {
    try {
      // This should be the only http request for home page, for health check purposes
      fetch(backend + '/success', {
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
        <div className="button-group">
          <Button to={frontendSlowdown ? '/products-fes' : '/products'}>
            Browse products
          </Button>
          <Button to="/specials">
            Browse specials
          </Button>
        </div>
      </div>
    </div>
  );
}

export default Home;
