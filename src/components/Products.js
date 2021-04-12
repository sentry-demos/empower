import { Link } from 'react-router-dom';
import './products.css';

function Products(props) {
  const addProductToCart = (product) => {
    const newCart = [...props.cart, product];
    props.setCart(newCart);
  };

  return (
    <div>
      <h1>Products catalog</h1>

      <ul className="products-list">
        {props.products.map((product) => {
          return (
            <li>
              <Link to="/product/1">
                <img src="https://via.placeholder.com/500x250" alt="product" />
                <div>
                  <h2>{product.title}</h2>
                  <p className="product-description">{product.description}</p>
                </div>
              </Link>
              <div>
                <p className="price">${product.price}.00</p>
                <button onClick={() => addProductToCart(product)}>
                  Add to cart
                </button>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default Products;
