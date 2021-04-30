import { useContext, Component } from 'react';
import { Context } from '../index';
import { Link } from 'react-router-dom';
import * as Sentry from '@sentry/react';
import './products.css';

// https://stackoverflow.com/questions/55896644/react-usecontext-throws-invalid-hook-call-error/55896816
// https://stackoverflow.com/questions/56734758/why-usecontext-doest-work-in-my-function
// https://medium.com/javascript-scene/do-react-hooks-replace-redux-210bab340672

// NEW CODE
class Products extends Component {
  constructor(props) {
    console.log('contructor')
  }
  static contextType = Context;
  
  render() {
    const { cart, products } = useContext(Context);
      return (
        <div>
          <ul className="products-list">
            {products.map((product) => {
              const itemLink = '/product/' + product.id;
              return (
                <li key={product.id}>
                  <div>
                    <Link to={itemLink}>
                      <img src={product.img} alt="product" />
                      <div>
                        <h2>{product.title}</h2>
                        <p className="product-description">{product.description}</p>
                      </div>
                    </Link>
                    <button onClick={() => cart.update({ action: 'add', product })}>
                      Add to cart — ${product.price}.00
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      );
  }
}
export default Sentry.withProfiler(Products, { name: "Products"})

// OLD CODE
// function Products() {
//   const { cart, products } = useContext(Context);
//   return (
//     <div>
//       <ul className="products-list">
//         {products.map((product) => {
//           const itemLink = '/product/' + product.id;
//           return (
//             <li key={product.id}>
//               <div>
//                 <Link to={itemLink}>
//                   <img src={product.img} alt="product" />
//                   <div>
//                     <h2>{product.title}</h2>
//                     <p className="product-description">{product.description}</p>
//                   </div>
//                 </Link>
//                 <button onClick={() => cart.update({ action: 'add', product })}>
//                   Add to cart — ${product.price}.00
//                 </button>
//               </div>
//             </li>
//           );
//         })}
//       </ul>
//     </div>
//   );
// }
// // export default Products;
// export default Sentry.withProfiler(Products, { name: "Products"})



