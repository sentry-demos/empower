import { Link } from 'react-router-dom';

function Button(props) {
  return (
    <Link {...props} className="btn">
      {props.children}
    </Link>
  );
}

export default Button;
