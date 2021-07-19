import { Component } from 'react';
import { Link } from 'react-router-dom';

class Button extends Component {
  render() {
    var className = this.props.visibility === "hidden" ? "btn-hidden": "btn"
    return (
      <Link {...this.props} className={className}>
        {this.props.children}
      </Link>
    );
  }
}

export default Button;
