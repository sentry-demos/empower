import { Link } from 'react-router-dom';

function Products() {
  return (
    <div>
      <h2>Products Page Here</h2>
      <Link to="/product/1">Product/:id</Link>
    </div>
  );
}

export default Products;
