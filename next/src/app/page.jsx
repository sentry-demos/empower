'use client'

import * as Sentry from '@sentry/nextjs';
import plantsBackground from '/public/plants-background-img.jpg';
import ButtonLink from '/src/ui/ButtonLink';
import { useSearchParams } from 'next/navigation';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  determineBackendType,
  determineBackendUrl,
} from '/src/utils/backendrouter';

const divStyle = {
  backgroundImage: 'url(' + plantsBackground.src + ')',
};


export default function Page(props) {

  console.log("in home page");
  const router = useRouter();
  const { backend } = useSearchParams();
  const backendType = determineBackendType(backend);
  const backendUrl = determineBackendUrl(backendType);
  console.log('backend is ' + backendUrl);
  const [showSuggestionFeature, setShowSuggestionFeature] = useState(false);

  const [suggestion, setSuggestion] = useState("");
  const [city, setCity] = useState("");

  const handleInputChange = (e) => {
    setCity(e.target.value);
  }

  const getShowSuggestionFeature = async () => {
    try {
      let resp = await fetch(`/api/showSuggestion`);
      let data = await resp.json()
      setShowSuggestionFeature(data.response)
    } catch (err) {
      console.error("Error checking for suggestion feature");
    }
  }


  const getSuggestion = async () => {
    console.log("Fetching suggestion...")
    try {
      let resp = await fetch(`/api/suggestion?geo=${city}`);
      console.log(resp);
      let data = await resp.json();
      setSuggestion(data.suggestion);
      console.log(data.suggestion);
      const ele = document.getElementById('hero-suggestion');
      ele.classList.add("fade-in");

    } catch (err) {
      console.error("Error fetching suggestion", err);
    }
  }

  useEffect(() => {
    try {
      // This should be the only http request for home page, for health check purposes
      fetch(backendUrl + '/success', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      getShowSuggestionFeature();
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
        {showSuggestionFeature &&
          <div>
            <button onClick={getSuggestion}>
              Get Suggestion
            </button>

            {!suggestion &&
              <input
                className="city-input"
                name="city"
                placeholder="Your City"
                onChange={handleInputChange}
              />}
            <div id="hero-suggestion">
              <p>{suggestion}</p>
            </div>
          </div>}
      </div>
    </div>
  );
}
