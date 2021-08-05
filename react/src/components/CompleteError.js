import { Component } from 'react';
import { Link } from 'react-router-dom';
import './complete.css';

class CompleteError extends Component {
  render() {
    let errorInfo = this.props.history.location.state
    console.log("> errorInfo", errorInfo)

    return (
      <div className="checkout-container-complete">
        <h2>We're having some trouble</h2>
        <p>
          We were unable to process your order but will do everything we can to
          make it right. Please <Link to="/">reach out to us</Link> if you have
          been charged or have any questions.
        </p>
      </div>
    );
  }
}

export default CompleteError;
