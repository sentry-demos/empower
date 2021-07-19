import { Component } from 'react';
import { Link } from 'react-router-dom';

class Button extends Component {
  render() {
    return (
      <Link {...this.props} className="btn" style={{visibility: this.props.visibility}}>
        {this.props.children}
      </Link>
    );
  }
}

export default Button;
