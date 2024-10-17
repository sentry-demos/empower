import Link from 'next/link';

function Button({ to, children, params }) {
  console.log(params);
  const hrefLink = {
    pathname: to,
    query: params,
  };
  console.log(to);
  console.log(children);
  return (
    <Link href={hrefLink} className="btn">
      {children}
    </Link>
  );
}

export default Button;
