import * as Sentry from '@sentry/react';
import plantsBackground from '../assets/plants-background-img.jpg';
import Button from './ButtonLink';
import ChatWidget from './ChatWidget';
import { useEffect, useState } from 'react';

const divStyle = {
  backgroundImage: 'url(' + plantsBackground + ')',
};

function Home({ frontendSlowdown, backend }) {
  // Which of the two things the home page can be: the hero, or the agent
  // conversation that replaces it. The floating chat button stays available in
  // both, so this is an addition to the entry points rather than a change to
  // them — see the note in ChatWidget.jsx about test_ai_agent.py.
  const [agentView, setAgentView] = useState(false);

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

  if (agentView) {
    return <ChatWidget fullView onExitFull={() => setAgentView(false)} />;
  }

  return (
    <div className="hero sentry-unmask">
      <div className="hero-bg-img" style={divStyle}></div>
      <div className="hero-content">
        <h1>Empower your plants</h1>
        <p>Keep your houseplants happy.</p>
        <div className="hero-actions">
          <Button to={frontendSlowdown ? '/products-fes' : '/products'}>
            Browse products
          </Button>
          <button
            type="button"
            id="home-ask-agent"
            className="btn hero-agent-button sentry-unmask"
            onClick={() => {
              Sentry.metrics.count('chat.open', 1, {
                attributes: { source: 'hero_button' },
              });
              setAgentView(true);
            }}
          >
            Ask our plant agent
          </button>
        </div>
      </div>
      <ChatWidget />
    </div>
  );
}

export default Home;
