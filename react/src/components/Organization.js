import { Component } from 'react';
import logo from '../assets/logo.svg';
import './Organization.css';
import * as Sentry from '@sentry/react';
import { isOddReleaseWeek, busy_sleep } from '../utils/time';

class Organization extends Component {
  constructor() {
    super();
    // must be inside the constructor to affect LCP, if in componentDidMount() only affects duration
    if (isOddReleaseWeek()) {
      // can't have async sleep in a constructor
      busy_sleep(Math.random(40) + 150);
    }
  }

  componentDidMount() {
    // Must bust cache to have force transfer size
    // small compressed file
    let uc_small_script = document.createElement('script');
    uc_small_script.async = false;
    uc_small_script.src =
      this.props.backend +
      '/compressed_assets/compressed_small_file.js' +
      '?cacheBuster=' +
      Math.random();
    document.body.appendChild(uc_small_script);

    // big uncompressed file
    let c_big_script = document.createElement('script');
    c_big_script.async = false;

    c_big_script.src =
      this.props.backend +
      '/uncompressed_assets/uncompressed_big_file.js' +
      '?cacheBuster=' +
      Math.random();
    document.body.appendChild(c_big_script);
  }

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

export default Sentry.withProfiler(Organization, { name: 'Organization' });
