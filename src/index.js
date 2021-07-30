import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import "react-loader-spinner/dist/loader/css/react-spinner-loader.css";
import * as Sentry from '@sentry/react';
import { Integrations } from '@sentry/tracing';
import Context from './utils/context';
import { createBrowserHistory } from 'history';
import { Router, Switch, Route } from 'react-router-dom';

import { Provider } from 'react-redux'
import { createStore, applyMiddleware, compose } from 'redux'
import logger from 'redux-logger'
import rootReducer from './reducers'

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

const sentryReduxEnhancer = Sentry.createReduxEnhancer({});

const store = createStore(
  rootReducer,
  compose(applyMiddleware(logger), sentryReduxEnhancer)
)

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

      new PerformanceObserver(entryList => {
        console.log(entryList.getEntries());
      }).observe({ type: "largest-contentful-paint", buffered: true });
    })
  }


  render() {
    return (
        <Provider
          store={store}
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
        </Provider>
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
