import { Component } from 'react';
import Context from '../utils/context';
//import { Link } from 'react-router-dom';
import './products.css';
import * as Sentry from '@sentry/react';
import { connect } from 'react-redux'
import { setProducts, addProduct } from '../actions'
import Loader from "react-loader-spinner";
import { busy_sleep } from "../utils/time"
import ProductCard from './ProductCard'

class Products extends Component {
  static contextType = Context;

  constructor() {
    super();
    // makes the ui.react.mount span widen to 1500ms
    busy_sleep(1500)
  }

  // getProducts handles error responses differently, depending on the browser used
  async getProducts() {
    let se, customerType, email
    Sentry.withScope(function(scope) {
      [ se, customerType ] = [scope._tags.se, scope._tags.customerType ]
      email = scope._user.email
    });

    ['/api', '/connect', '/organization'].forEach((endpoint) => {
      fetch(this.props.backend + endpoint, {
        method: "GET",
        headers: { se, customerType, email, "Content-Type": "application/json" }
      })
        .catch((err) => { 
          // If there's an error, it won't stop the Products http request and page from loading
          Sentry.captureException(err)
        })
    })

    let result = await fetch(this.props.backend + "/products", {
      method: "GET",
      headers: { se, customerType, email, "Content-Type": "application/json" }
    })
      .catch((err) => { 
        return { ok: false, status: 500}
      })

    if (!result.ok) {
      Sentry.configureScope(function(scope) {
        Sentry.setContext("err", {
          status: result.status,
          statusText: result.statusText
        })
      });
      return Promise.reject();
    } else {
      const jsonValue = await result.json()
      return Promise.resolve(jsonValue)
    }
  }

  async shouldComponentUpdate() {
    console.log("> Products shouldComponentUpdate")
  }

  async componentDidMount(){
    var products
    try {
      products = await this.getProducts();
      // take first 4 products because that's all we have img/title/description for
      this.props.setProducts(products.slice(0,4))
    } catch(err) {
      Sentry.captureException(new Error("app unable to load products: " + err));
    }
  }

  render() {
    const { products } = this.props;
    return products.length > 0 ? (
      <div>
        <ul className="products-list">
          {products.map((product) => {
            //const itemLink = '/product/' + product.id;
            const averageRating = (product.reviews.reduce((a,b) => a + (b["rating"] || 0),0) / product.reviews.length).toFixed(1)

            let stars = [1,2,3,4,5].map((index) => {
              if (index <= averageRating) {
                return (<span className="star" key={index}>&#9733;</span>)
              } else {
                return (<span className="star" key={index}>&#9734;</span>)
              }
            })

            return (
              <ProductCard key={product.id} product={product} stars={stars}></ProductCard>
            );
          })}
        </ul>
      </div>
    ) : (
      <div className="loader-container">
        <Loader
          type="ThreeDots"
          color="#f6cfb2"
          height={150}
          width={150}
          />
      </div>
    )
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
)(Sentry.withProfiler(Products, { name: "Products"}))
