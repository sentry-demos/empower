import { Component } from 'react';
import Context from '../utils/context';
import { Link } from 'react-router-dom';
import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux'
import { setProducts, addProduct } from '../actions'
import Loader from "react-loader-spinner";

class ProductsTreeItem extends Component {
  static contextType = Context;

  render() {
    console.log("TreeItem props", this.props.product1)
    // const { products } = this.props;

    return <div>HI</div>

    // return (
    //     <li key={product.id}>
    //         <div>
    //         <Link to={itemLink}>
    //             <img src={product.img} alt="product" />
    //             <div>
    //             <h2>{product.title}</h2>
    //             <p className="product-description">
    //                 {product.description}
    //             </p>
    //             </div>
    //         </Link>
    //         <button
    //             onClick={() => this.props.addProduct(product)}
    //         >
    //             Add to cart — ${product.price}.00
    //         </button>
    //         <p>{stars} ({product.reviews.length})</p>
    //         </div>
    //     </li>
    // )

    // return products.length > 0 ? (
    //   <div>
    //     <ul className="products-list">
    //       {products.map((product) => {
    //         const itemLink = '/product/' + product.id;
    //         const averageRating = (product.reviews.reduce((a,b) => a + (b["rating"] || 0),0) / product.reviews.length).toFixed(1)

    //         let stars = [1,2,3,4,5].map((index) => {
    //           if (index <= averageRating) {
    //             return (<span className="star" key={index}>&#9733;</span>)
    //           } else {
    //             return (<span className="star" key={index}>&#9734;</span>)
    //           }
    //         })

    //         return (
    //           <ProductsTreeItem></ProductsTreeItem>
    //         );
    //       })}
    //     </ul>
    //   </div>
    // ) : (
    //   <div className="loader-container">
    //     <Loader
    //       type="ThreeDots"
    //       color="#f6cfb2"
    //       height={150}
    //       width={150}
    //       />
    //   </div>
    // )
  }
}


const mapStateToProps = (state, ownProps) => {
    return {
      cart: state.cart,
      products: state.products
    }
  }
  
export default connect(
    mapStateToProps,
    { setProducts, addProduct }
)(Sentry.withProfiler(ProductsTreeItem, { name: "ProductsTreeItem"}))
  