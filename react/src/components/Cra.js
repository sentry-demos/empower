import { Component } from 'react';
import logo from '../assets/logo.svg';
import './Cra.css';
import * as Sentry from '@sentry/react';
class Cra extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <p>
            So you can see how a html header, logo svg and css were used by
            default.
          </p>
          <a
            className="App-link"
            href="https://reactjs.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn React
          </a>
        </header>
      </div>
    );
  }
}

export default Sentry.withProfiler(Cra, { name: "Cra"})
