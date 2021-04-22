import React, { useReducer } from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import * as Sentry from '@sentry/react';
import { Integrations } from '@sentry/tracing';
import { createBrowserHistory } from 'history';
import { BrowserRouter as Router, Switch, Route, Link } from 'react-router-dom';
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

import Button from './components/Button';
import Footer from './components/Footer';
import Nav from './components/Nav';

import ScrollToTop from './components/ScrollToTop';

import EPlogo from './assets/empowerplant-logo.svg';
import plantsBackground from './assets/plants-background-img.jpg';

import productOne from './components/products/1';
import productTwo from './components/products/2';
import productThree from './components/products/3';
import productFour from './components/products/4';

const tracingOrigins = ['localhost', 'empowerplant.io', /^\//];

const history = createBrowserHistory();
const SentryRoute = Sentry.withSentryRouting(Route);

Sentry.init({
  dsn:
    'https://19349cefec81421f89ba3c572f5a1f59@o262702.ingest.sentry.io/5711949',
  integrations: [
    new Integrations.BrowserTracing({
      tracingOrigins: tracingOrigins,
      routingInstrumentation: Sentry.reactRouterV5Instrumentation(history),
    }),
  ],
  tracesSampleRate: 1.0,
  release: new Date().getMonth() + '.' + new Date().getDate(),
  environment: 'test',
  beforeSend(event) {
    return event;
  },
});

const cartReducer = (state, { action, product }) => {
  if (!product) throw new Error('Cart reducer requires a product');

  const newState = { ...state };

  switch (action) {
    case 'add': {
      let item = newState.items.find((x) => x.id === product.id);
      if (!item) newState.items.push(product);
      newState.quantities[product.id] = newState.quantities[product.id] || 0;
      newState.quantities[product.id]++;
      break;
    }
    case 'remove': {
      let item = newState.items.find((x) => x.id === product.id);
      if (!item) return newState;
      newState.quantities[product.id]--;
      if (newState.quantities[product.id] === 0) {
        delete newState.quantities[product.id];
        const i = newState.items.findIndex((x) => x.id === product.id);
        newState.items.splice(i, 1);
      }
      break;
    }
    default:
      throw new Error('Unknown cart action');
  }

  newState.total = newState.items.reduce((a, item) => {
    const itemTotal = item.price * newState.quantities[item.id];
    return a + itemTotal;
  }, 0);

  return newState;
};

export const Context = React.createContext({
  products: [],
  cart: { items: [] },
});

const App = (props) => {
  const [cart, dispatch] = useReducer(cartReducer, {
    items: [],
    quantities: {},
    total: 0,
  });

  return (
    <React.StrictMode>
      <Context.Provider
        value={{
          cart: { ...cart, update: dispatch },
          products: [productOne, productTwo, productThree, productFour],
        }}
      >
        <Router history={history}>
          <Nav />

          <div id="body-container">
            <ScrollToTop />
            <Switch>
              <Route exact path="/" component={Home} />
              <Route path="/about" component={About} />
              <Route path="/cart" component={Cart} />
              <Route path="/checkout" component={Checkout} />
              <Route path="/complete" component={Complete} />
              <Route path="/error" component={CompleteError} />
              <Route path="/cra" component={Cra} />
              <SentryRoute
                path="/employee/:name"
                component={Employee}
              ></SentryRoute>
              <SentryRoute
                path="/product/:id"
                component={Product}
              ></SentryRoute>
              <Route path="/products">
                <Products />
              </Route>
              <Route component={NotFound} />
            </Switch>
          </div>

          <Footer />
        </Router>
      </Context.Provider>
    </React.StrictMode>
  );
};

// React-router in use here https://reactrouter.com/web/guides/quick-start
ReactDOM.render(<App />, document.getElementById('root'));

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
