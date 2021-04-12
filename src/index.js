import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import About from './components/About';
import Checkout from './components/Checkout';
import Cra from './components/Cra';
import Employee from './components/Employee';
import NotFound from './components/NotFound';
import Product from './components/Product';
import Products from './components/Products';
import * as Sentry from '@sentry/react';
import { Integrations } from '@sentry/tracing';
import { createBrowserHistory } from 'history';

import productOne from './components/products/1';

import { BrowserRouter as Router, Switch, Route, Link } from 'react-router-dom';

import logo from './assets/logo.svg';

// from Creat New React App
// ReactDOM.render(
//   <React.StrictMode>
//     <AppOld />
//   </React.StrictMode>,
//   document.getElementById('root')
// );

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

const App = () => {
  const [products, setProducts] = useState([productOne]);
  const [cart, setCart] = useState([]);
  console.log(products);

  return (
    <React.StrictMode>
      <Router history={history}>
        <nav id="top-nav">
          <Link to="/" id="home-link">
            <img src={logo} className="logo" alt="logo" />
            Empower Plant
          </Link>

          <div id="top-right-links">
            <Link to="/products">Products</Link>
            <Link to="/checkout">Checkout</Link>
          </div>
        </nav>

        <div id="body-container">
          <Switch>
            <Route exact path="/" component={Home} />
            <Route path="/about" component={About} />
            <Route path="/checkout" component={Checkout} />
            <Route path="/cra" component={Cra} />
            <SentryRoute
              path="/employee/:name"
              component={Employee}
            ></SentryRoute>
            <SentryRoute path="/product/:id" component={Product}></SentryRoute>
            <Route path="/products">
              <Products
                products={products}
                cart={cart}
                setCart={setCart}
              ></Products>
            </Route>
            <Route component={NotFound} />
          </Switch>
        </div>

        <footer id="footer">
          <div>
            <h2>Sign up for plant tech news</h2>
            <form>
              <label for="email-subscribe">Email</label>
              <input
                type="email"
                name="email-subscribe"
                id="email-subscribe"
              ></input>
              <input type="submit" value="Subscribe"></input>
            </form>
          </div>
        </footer>
      </Router>
    </React.StrictMode>
  );
};

// React-router in use here https://reactrouter.com/web/guides/quick-start
ReactDOM.render(<App />, document.getElementById('root'));

function Home() {
  return (
    <div className="hero">
      <h1>Empower your plants</h1>
      <p>Keep your houseplants happy.</p>
      <Link to="/products">Browse Products</Link>
    </div>
  );
}
