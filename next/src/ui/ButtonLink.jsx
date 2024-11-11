import Link from 'next/link';

function Button({ to, children, params }) {
  const hrefLink = {
    pathname: to,
    query: params,
  };
  return (
    <Link href={hrefLink} className="btn">
      {children}
    </Link>
  );
}

export default Button;
