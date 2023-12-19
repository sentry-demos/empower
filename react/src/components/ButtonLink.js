import { Link } from 'react-router-dom';

function Button() {
  return (
    <Link {...this.props} className="btn">
      {this.props.children}
    </Link>
  );
}

export default Button;
