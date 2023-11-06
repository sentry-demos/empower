import * as Sentry from '@sentry/react';
import { Fragment, Component } from 'react';
import { Link } from 'react-router-dom';
import './footer.css';

class Footer extends Component {
  state = {
    subscribed: false,
  };

  async shouldComponentUpdate() {
    console.log('> Footer shouldComponentUpdate');
  }

  render() {
    const handleSubscribeClick = () => {
      this.setState({ subscribed: true });
    };

    return (
      <footer id="footer">
        <div>
          <h2 className="h3 sentry-unmask">Sign up for plant tech news</h2>
          <Sentry.ErrorBoundary
            onReset={() => {
              this.setState({ subscribed: false });
            }}
            fallback={({ resetError, eventId }) => {
              return (
                <Fragment>
                  <div>An error has occurred. Sentry Event ID: {eventId}</div>
                  <button className="btn" onClick={resetError}>
                    Reset Form
                  </button>
                </Fragment>
              );
            }}
          >
            <div className="formContainer">
              <form>
                <label htmlFor="email-subscribe" className="sentry-unmask">
                  Email
                </label>
                <input
                  type="email"
                  name="email-subscribe"
                  id="email-subscribe"
                ></input>
              </form>
              <input
                type="submit"
                value="Subscribe"
                className="sentry-unmask"
                onClick={handleSubscribeClick}
              />
              {this.state.subscribed && <SubscribedMessage />}
            </div>
          </Sentry.ErrorBoundary>
          <p className="sentry-unmask">
            © 2021 • Empower Plant • <Link to="/about">About us</Link>
          </p>
        </div>
      </footer>
    );
  }
}

function SubscribedMessage() {
  throw new Error('SubscribedMessage error');
}

export default Footer;
