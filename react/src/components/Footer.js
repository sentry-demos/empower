import { Component } from 'react';
import { Link } from 'react-router-dom';
import './footer.css';

class Footer extends Component {
  async shouldComponentUpdate() {
    console.log("> Footer shouldComponentUpdate")
  }

  render() {
    return (
      <footer id="footer">
        <div>
          <h2 className="h3">Sign up for plant tech news</h2>
          <form>
            <label htmlFor="email-subscribe">Email</label>
            <input
              type="email"
              name="email-subscribe"
              id="email-subscribe"
            ></input>
            <input type="submit" value="Subscribe"></input>
          </form>
          <p>
            © 2021 • Empower Plant • <Link to="/about">About us</Link>
          </p>
        </div>
      </footer>
    );
  }
}

export default Footer;
