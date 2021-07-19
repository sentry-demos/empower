import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import * as Sentry from '@sentry/react';
import { Integrations } from '@sentry/tracing';
import Context from './utils/context';
import { createBrowserHistory } from 'history';
import { Router, Switch, Route } from 'react-router-dom';

import ScrollToTop from './components/ScrollToTop';
import Button from './components/ButtonLink';
import Footer from './components/Footer';
import Nav from './components/Nav';
import About from './components/About';
import Cart from './components/Cart';
import Checkout from './components/Checkout';
import Complete from './components/Complete';
import CompleteError from './components/CompleteError';
import Cra from './components/Cra';
import Employee from './components/Employee';
import NotFound from './components/NotFound';
import Product from './components/Product';
import Products from './components/Products';
import ProductsJoin from './components/ProductsJoin';

import plantsBackground from './assets/plants-background-img.jpg';

const tracingOrigins = ['localhost', 'empowerplant.io', 'run.app', 'appspot.com', /^\//];

const history = createBrowserHistory();
const SentryRoute = Sentry.withSentryRouting(Route);

let ENVIRONMENT
console.log("window.location", window.location)
if (window.location.hostname === "localhost") {
  ENVIRONMENT = "test"
} else { // App Engine
  ENVIRONMENT = "production"
}
const DSN = process.env.REACT_APP_DSN
const RELEASE = process.env.REACT_APP_RELEASE
console.log("ENVIRONMENT", ENVIRONMENT)
console.log("RELEASE", RELEASE)

Sentry.init({
  dsn: DSN,
  integrations: [
    new Integrations.BrowserTracing({
      tracingOrigins: tracingOrigins,
      routingInstrumentation: Sentry.reactRouterV5Instrumentation(history),
    }),
  ],
  tracesSampleRate: 1.0,
  release: RELEASE,
  environment: ENVIRONMENT,
  beforeSend(event) {
    return event;
  }
});

class App extends Component {
  
  constructor() {
    super();
    this.state = {
      cart: {
        items: [],
        quantities: {},
        total: 0,
      },
      products: {
        response: []
      }
    };

    this.cartReducer = this.cartReducer.bind(this);
    this.productsReducer = this.productsReducer.bind(this);
    // These also get passed via request headers
    Sentry.configureScope(scope => {
      
      const customerType = ["medium-plan", "large-plan", "small-plan", "enterprise"][Math.floor(Math.random() * 4)]
      scope.setTag("customerType", customerType )
      
      let queryParam = history.location.search
      if (queryParam.includes("se=")) {
        const se = queryParam.split("se=").pop()
        console.log("se", se)
        scope.setTag("se", se)
      }

      let email = Math.random().toString(36).substring(2, 6) + "@yahoo.com";
      scope.setUser({ email: email })
    })
  }

  productsReducer({ action, response }) {
    if (!response) throw new Error('Products reducer requires a response');
    
    const products = { ...this.state.products };

    switch (action) {
      case 'add': {
        products.response = response
        // products = response // <-- prefer to use this, but get error "products.map is not a function" in Products.js
        break;
      }
      default:
        throw new Error('Unknown products action');
    }
    this.setState({ products })
  }
  cartReducer({ action, product }) {
    if (!product) throw new Error('Cart reducer requires a product');

    const cart = { ...this.state.cart };

    switch (action) {
      case 'add': {
        let item = cart.items.find((x) => x.id === product.id);
        if (!item) cart.items.push(product);
        cart.quantities[product.id] = cart.quantities[product.id] || 0;
        cart.quantities[product.id]++;
        break;
      }
      case 'remove': {
        let item = cart.items.find((x) => x.id === product.id);
        if (!item) return cart;
        cart.quantities[product.id]--;
        if (cart.quantities[product.id] === 0) {
          delete cart.quantities[product.id];
          const i = cart.items.findIndex((x) => x.id === product.id);
          cart.items.splice(i, 1);
        }
        break;
      }
      default:
        throw new Error('Unknown cart action');
    }

    cart.total = cart.items.reduce((a, item) => {
      const itemTotal = item.price * cart.quantities[item.id];
      return a + itemTotal;
    }, 0);

    this.setState({ cart });
  }

  render() {
    return (
        <Context.Provider
          value={{
            cart: { ...this.state.cart, update: this.cartReducer },
            // products: [productOne, productTwo, productThree, productFour],
            products: { ...this.state.products, update: this.productsReducer }
          }}
        >
          <Router history={history}>
            <ScrollToTop />
            <Nav />

            <div id="body-container">
              <Switch>
                <Route exact path="/" component={Home} />
                <Route path="/about" component={About} />
                <Route path="/cart" component={Cart} />
                <Route path="/checkout" component={Checkout} />
                <Route path="/complete" component={Complete} />
                <Route path="/error" component={CompleteError} />
                <Route path="/cra" component={Cra} />
                <SentryRoute path="/employee/:slug" component={Employee}></SentryRoute>
                <SentryRoute path="/product/:id" component={Product}></SentryRoute>
                <Route path="/products" component={Products} />
                <Route path="/products-join" component={ProductsJoin} />
                <Route component={NotFound} />
              </Switch>
            </div>
            <Footer />
          </Router>
        </Context.Provider>
    );
  }
}

// React-router in use here https://reactrouter.com/web/guides/quick-start
ReactDOM.render(<App />, document.getElementById('root'));

// See Transaction for everything you get, without any xhr/ajax requests going on.
// This page doesn't have any, it's pure static content
function Home() {
  const divStyle = {
    backgroundImage: 'url(' + plantsBackground + ')',
  };
  return (
    <div className="hero">
      <div className="hero-bg-img" style={divStyle}></div>
      <div className="hero-content">
        <h1>Empower your plants</h1>
        <p>Keep your houseplants happy.</p>
        <Button to="/products">Browse products</Button>
      </div>
    </div>
  );
}

