import React, { Component, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import 'react-loader-spinner/dist/loader/css/react-spinner-loader.css';
import * as Sentry from '@sentry/react';
import { createBrowserHistory } from 'history';
import {
  Routes,
  Route,
  BrowserRouter,
  useLocation,
  useNavigationType,
  createRoutesFromChildren,
  matchRoutes,
} from 'react-router-dom';
import { crasher } from './utils/errors';
import ErrorBoundary from './components/ErrorBoundary';
import {
  determineBackendType,
  determineBackendUrl,
} from './utils/backendrouter';

import { Provider } from 'react-redux';
import { createStore, applyMiddleware, compose } from 'redux';
import logger from 'redux-logger';
import rootReducer from './reducers';

import ScrollToTop from './components/ScrollToTop';
import Footer from './components/Footer';
import Nav from './components/Nav';
import About from './components/About';
import Cart from './components/Cart';
import Checkout from './components/Checkout';
import Complete from './components/Complete';
import CompleteError from './components/CompleteError';
import Employee from './components/Employee';
import Home from './components/Home';
import NotFound from './components/NotFound';
import Product from './components/Product';
import Products from './components/Products';
import ProductsJoin from './components/ProductsJoin';
import Nplusone from './components/nplusone';

const tracingOrigins = [
  'localhost',
  'empowerplant.io',
  'run.app',
  'appspot.com',
  /^\//,
];

const history = createBrowserHistory();

let ENVIRONMENT;
if (window.location.hostname === 'localhost') {
  ENVIRONMENT = 'test';
} else {
  // App Engine
  ENVIRONMENT = 'production';
}

let BACKEND_URL;
let FRONTEND_SLOWDOWN;
let RAGECLICK;
const DSN = process.env.REACT_APP_DSN;
const RELEASE = process.env.REACT_APP_RELEASE;

console.log('ENVIRONMENT', ENVIRONMENT);
console.log('RELEASE', RELEASE);

Sentry.init({
  dsn: DSN,
  release: RELEASE,
  environment: ENVIRONMENT,
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
  replaysSessionSampleRate: 1.0,
  debug: true,
  integrations: [
    Sentry.feedbackIntegration({
      // Additional SDK configuration goes in here, for example:
      colorScheme: 'system',
    }),
    new Sentry.metrics.MetricsAggregator(),
    new Sentry.BrowserProfilingIntegration(),
    new Sentry.BrowserTracing({
      tracingOrigins: tracingOrigins,
      tracePropagationTargets: tracingOrigins,
      routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes
      ),
      beforeNavigate: (context) => {
        const { name, op } = context;

        const { source } = context.metadata;

        if (source === 'url' && (name === '/' || name === '/checkout')) {
          context.metadata.source = 'route';
        }

        return {
          ...context,
          // How to parameterize a transaction if not using a Routing library
          // name: window.location.pathname.replace(/\/employee.*/,'/employee/:id')
        };
      },
      _experiments: {
        // This enables tracing on user interactions like clicks
        //  --> 2/13/24 disabling experimental interactions feature
        //      because it may be preventing navigation transactions
        //      from being captured
        enableInteractions: false,
        // This enables profiling of route transactions in react
        onStartRouteTransaction: Sentry.onProfilingStartRouteTransaction,
      },
    }),
    new Sentry.Replay({
      // Additional configuration goes in here
      // replaysSessionSampleRate and replaysOnErrorSampleRate is now a top-level SDK option
      blockAllMedia: false,
      // https://docs.sentry.io/platforms/javascript/session-replay/configuration/#network-details
      networkDetailAllowUrls: ['/checkout', '/products'],
    }),
  ],
  beforeSend(event, hint) {
    // Parse from tags because src/index.js already set it there. Once there are React route changes, it is no longer in the URL bar
    let se;
    Sentry.withScope(function (scope) {
      se = scope._tags.se;
    });

    if (se) {
      const seTdaPrefixRegex = /[^-]+-tda-[^-]+-/;
      let seFingerprint = se;
      let prefix = seTdaPrefixRegex.exec(se);
      if (prefix) {
        // Now that TDA puts platform/browser and test path into SE tag we want to prevent
        // creating separate issues for those. See https://github.com/sentry-demos/empower/pull/332
        seFingerprint = prefix[0];
      }
      if (se.startsWith('prod-tda-')) {
        // Release Health
        event.fingerprint = ['{{ default }}', seFingerprint, RELEASE];
      } else {
        // SE Testing
        event.fingerprint = ['{{ default }}', seFingerprint];
      }
    }

    if (event.exception) {
      sessionStorage.setItem('lastErrorEventId', event.event_id);
    }

    return event;
  },
});

// TODO is this best placement?
const SentryRoutes = Sentry.withSentryReactRouterV6Routing(Routes);

const sentryReduxEnhancer = Sentry.createReduxEnhancer({});

const store = createStore(
  rootReducer,
  compose(applyMiddleware(logger), sentryReduxEnhancer)
);

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
        response: [],
      },
    };

    let queryParams = new URLSearchParams(history.location.search);

    // Set desired backend
    let backendTypeParam = queryParams.get('backend');
    const backendType = determineBackendType(backendTypeParam);
    BACKEND_URL = determineBackendUrl(backendType, ENVIRONMENT);

    console.log(`> backendType: ${backendType} | backendUrl: ${BACKEND_URL}`);

    // These also get passed via request headers (see window.fetch below)
    Sentry.configureScope((scope) => {
      const customerType = [
        'medium-plan',
        'large-plan',
        'small-plan',
        'enterprise',
      ][Math.floor(Math.random() * 4)];
      scope.setTag('customerType', customerType);

      if (queryParams.get('se')) {
        // Route components (navigation changes) will now have 'se' tag on scope
        console.log('> src/index.js se', queryParams.get('se'));
        scope.setTag('se', queryParams.get('se'));
        // for use in Checkout.js when deciding whether to pre-fill form
        // lasts for as long as the tab is open
        sessionStorage.setItem('se', queryParams.get('se'));
      }

      if (queryParams.get('frontendSlowdown') === 'true') {
        console.log('> frontend-only slowdown: true');
        FRONTEND_SLOWDOWN = true;
        scope.setTag('frontendSlowdown', true);
      } else {
        console.log('> frontend + backend slowdown');
        scope.setTag('frontendSlowdown', false);
      }

      if (queryParams.get('rageclick') === 'true') {
        RAGECLICK = true;
      }

      if (queryParams.get('userFeedback')) {
        sessionStorage.setItem('userFeedback', queryParams.get('userFeedback'));
      } else {
        sessionStorage.setItem('userFeedback', 'false');
      }
      sessionStorage.removeItem('lastErrorEventId');

      scope.setTag('backendType', backendType);

      let email = null;
      if (queryParams.get('userEmail')) {
        email = queryParams.get('userEmail');
      } else {
        // making fewer emails so event and user counts for an Issue are not the same
        let array = [
          'a',
          'b',
          'c',
          'd',
          'e',
          'f',
          'g',
          'h',
          'i',
          'j',
          'k',
          'l',
          'm',
          'n',
          'o',
          'p',
          'q',
          'r',
          's',
          't',
          'u',
          'v',
          'w',
          'x',
          'y',
          'z',
        ];
        let a = array[Math.floor(Math.random() * array.length)];
        let b = array[Math.floor(Math.random() * array.length)];
        let c = array[Math.floor(Math.random() * array.length)];
        email = a + b + c + '@example.com';
      }
      scope.setUser({ email: email });
    });

    // Automatically append `se`, `customerType` and `userEmail` query params to all requests
    // (except for requests to Sentry)
    const nativeFetch = window.fetch;
    window.fetch = function (...args) {
      let url = args[0];
      // When TDA is run in 'mock' mode inside Docker mini-relay will be ingesting on port 9989, see:
      // https://github.com/sentry-demos/empower/blob/79bed0b78fb3d40dff30411ef26c31dc7d4838dc/mini-relay/Dockerfile#L9
      let ignore_match = url.match(
        /^http[s]:\/\/([^.]+\.ingest\.sentry\.io\/|localhost:9989|127.0.0.1:9989).*/
      );
      if (!ignore_match) {
        Sentry.withScope(function (scope) {
          let se, customerType, email;
          [se, customerType] = [scope._tags.se, scope._tags.customerType];
          email = scope._user.email;
          args[1].headers = { ...args[1].headers, se, customerType, email };
        });
      }
      return nativeFetch.apply(window, args);
    };

    // Crasher parses query params sent by /tests for triggering crashes for Release Health
    crasher();
  }

  render() {
    return (
      <ErrorBoundary>
        <Provider store={store}>
          <BrowserRouter history={history}>
            <ScrollToTop />
            <Nav frontendSlowdown={FRONTEND_SLOWDOWN} />
            <div id="body-container">
              <SentryRoutes>
                <Route
                  path="/"
                  element={
                    <Home
                      backend={BACKEND_URL}
                      frontendSlowdown={FRONTEND_SLOWDOWN}
                    />
                  }
                ></Route>
                <Route
                  path="/about"
                element={<About backend={BACKEND_URL} history={history} />}
              ></Route>
              <Route path="/cart" element={<Cart />} />
              <Route
                path="/checkout"
                element={
                  <Checkout
                    backend={BACKEND_URL}
                    rageclick={RAGECLICK}
                    history={history}
                  />
                }
              ></Route>
              <Route path="/complete" element={<Complete />} />
              <Route path="/error" element={<CompleteError />} />
              <Route path="/employee/:id" element={<Employee />}></Route>
              <Route path="/product/:id" element={<Product />}></Route>
              <Route
                path="/products"
                element={<Products backend={BACKEND_URL} />}
              ></Route>
              <Route
                path="/products-fes" // fes = frontend slowdown (only frontend)
                element={
                  <Products backend={BACKEND_URL} frontendSlowdown={true} />
                }
              ></Route>
              <Route
                path="/nplusone"
                element={<Nplusone backend={BACKEND_URL} />}
              />
              <Route
                path="/products-join"
                element={<ProductsJoin backend={BACKEND_URL} />}
              ></Route>
              <Route path="*" element={<NotFound />} />
            </SentryRoutes>
          </div>
          <Footer />
        </BrowserRouter>
      </Provider>
    );
  }
}

// React-router in use here https://reactrouter.com/web/guides/quick-start
ReactDOM.render(<App />, document.getElementById('root'));
