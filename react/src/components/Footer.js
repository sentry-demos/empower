import { Component } from 'react';
import { Link } from 'react-router-dom';
import './footer.css';

class Footer extends Component {
  async shouldComponentUpdate() {
    console.log('> Footer shouldComponentUpdate');
  }

  render() {
    return (
      <footer id="footer">
        <div>
          <h2 className="h3 sentry-unmask">Sign up for plant tech news</h2>
          <div class="formContainer">
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
            ></input>
          </div>
          <p className="sentry-unmask">
            © 2021 • Empower Plant • <Link to="/about">About us</Link>
          </p>
        </div>
      </footer>
    );
  }
}

export default Footer;
