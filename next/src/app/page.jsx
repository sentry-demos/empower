'use client'

import * as Sentry from '@sentry/nextjs';
import plantsBackground from '/public/plants-background-img.jpg';
import ButtonLink from '/src/components/ButtonLink';
import { useSearchParams } from 'next/navigation';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  determineBackendType,
  determineBackendUrl,
} from '/src/utils/backendrouter';

const divStyle = {
  backgroundImage: 'url(' + plantsBackground.src + ')',
};


export default function Page() {
  console.log("in home page");
  const router = useRouter();
  const { backend, frontendSlowdown } = useSearchParams();
  const backendType = determineBackendType(backend);
  const backendUrl = determineBackendUrl(backendType);
  console.log('backend is ' + backendUrl);



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
        <ButtonLink to={'/products'} params={router.query}>
          Browse products
        </ButtonLink>
      </div>
    </div>
  );
}
