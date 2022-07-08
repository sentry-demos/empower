import { Component } from 'react';
import './complete.css';
import { Link } from 'react-router-dom';

class NotFound extends Component {
  async shouldComponentUpdate() {
    console.log("> NotFound shouldComponentUpdate")
  }

  render() {
    return (
      <div className="checkout-container-complete">
        <h2>404</h2>
        <p>
          The page you're looking for can't be found and we can't get to the
          root of it just yet. Please go back in your browser or go{' '}
          <Link to="/">back to our home page</Link> and accept our deepest
          apologies.
        </p>
        <p>
          If the issue persists, please <Link to="/">contact us</Link>.
        </p>
      </div>
    );
  }
}

export default NotFound;
// export default Sentry.withProfiler(NotFound, { name: "NotFound"})
