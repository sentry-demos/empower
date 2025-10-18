import React, { Component, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import 'react-loader-spinner/dist/loader/css/react-spinner-loader.css';
import * as Sentry from '@sentry/react';
import { statsigClient, updateStatsigUserAndEvaluate } from './utils/statsig';
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
  'empower-plant.com',
  'run.app',
  'appspot.com',
  /^\//,
];

const history = createBrowserHistory();

const PREFERRED_BACKENDS = ['flask', 'laravel'];

let BACKEND_URL;
let BACKEND_TYPE;
let FRONTEND_SLOWDOWN;
let RAGECLICK;
let PRODUCTS_API;
let PRODUCTS_EXTREMELY_SLOW;
let PRODUCTS_BE_ERROR;
let ADD_TO_CART_JS_ERROR;
let CHECKOUT_SUCCESS;
let ERROR_BOUNDARY;
const DSN = process.env.REACT_APP_DSN;
const RELEASE = process.env.REACT_APP_RELEASE;
const ENVIRONMENT = process.env.REACT_APP_ENVIRONMENT;

console.log('ENVIRONMENT', ENVIRONMENT);
console.log('RELEASE', RELEASE);



Sentry.init({
  dsn: DSN,
  release: RELEASE,
  environment: ENVIRONMENT,
  tracesSampleRate: 1.0,
  tracePropagationTargets: tracingOrigins,
  propagateTraceparent: true, // Sentry <-> OTLP distributed tracing
  profilesSampleRate: 1.0,
  replaysSessionSampleRate: 1.0,
  debug: true,
  enableLogs: true,
  beforeSendLog: (log) => {
    const tags = Sentry.getIsolationScope().getScopeData().tags;
    if ('user.email' in tags) {
      log.attributes['user.email'] = tags['user.email'];
    }
    return log;
  },
  integrations: (defaultIntegrations) => [
    // Filter out the Dedupe integration from the defaults
    ...defaultIntegrations.filter(integration => integration.name !== "Dedupe"),
    // Add custom integrations with options
    Sentry.feedbackIntegration({
      // Additional SDK configuration goes in here, for example:
      colorScheme: 'system',
    }),
    Sentry.browserProfilingIntegration(),
    Sentry.reactRouterV6BrowserTracingIntegration({
      useEffect,
      useLocation,
      useNavigationType,
      createRoutesFromChildren,
      matchRoutes,
    }),
    Sentry.replayIntegration({
      // Additional configuration goes in here
      // replaysSessionSampleRate and replaysOnErrorSampleRate is now a top-level SDK option
      blockAllMedia: false,
      // https://docs.sentry.io/platforms/javascript/session-replay/configuration/#network-details
      networkDetailAllowUrls: [/.*/],
      unmask: [".sentry-unmask"],
    }),
    Sentry.statsigIntegration({ featureFlagClient: statsigClient }),
    Sentry.consoleLoggingIntegration(), // All console logs are sent to Sentry
  ],
  beforeSend(event, hint) {
    // Parse from tags because src/index.js already set it there. Once there are React route changes, it is no longer in the URL bar
    let se;
    Sentry.withScope(function (scope) {
      se = scope._tags.se;
    });

    let is5xxError = event.exception && /^5\d{2} - .*$/.test(event.exception.values[0].value);
    if (se && is5xxError) {
      // Create a separate issue for each SE and RELEASE combination
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

    if ((PREFERRED_BACKENDS.includes(BACKEND_TYPE)) && is5xxError && (se && se.startsWith('prod-tda-'))) {
      // Seer when run automatically will use the latest event. We want it to run on event with flask backend instead of taking chances.
      event.fingerprint += ['tda-flagship-react-preferred-backends'];
    }

    if (event.exception) {
      sessionStorage.setItem('lastErrorEventId', event.event_id);
    }

    return event;
  },
});

await statsigClient.initializeAsync();

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
    BACKEND_TYPE = backendType;
    BACKEND_URL = determineBackendUrl(backendType);

    console.log(`> backendType: ${backendType} | backendUrl: ${BACKEND_URL}`);

    // These also get passed via request headers (see window.fetch below)

    // NOTE: because the demo extracts tags from the scope in order to pass them
    // as headers to the backend, we need to make sure we are calling `setTag()`
    // on the current scope. We don't want to call Sentry.setTag() as is usually
    // recommended (https://docs.sentry.io/platforms/javascript/enriching-events/scopes/#isolation-scope),
    // because that would set the tag on the isolation scope, and make it inaccessible
    // when it's time to set the headers.
    let currentScope = Sentry.getCurrentScope()

    const customerType = [
      'medium-plan',
      'large-plan',
      'small-plan',
      'enterprise',
    ][Math.floor(Math.random() * 4)];
    currentScope.setTag('customerType', customerType);

    let se = queryParams.get('se');
    if (se) {
      // Route components (navigation changes) will now have 'se' tag on scope
      currentScope.setTag('se', se);
      // for use in Checkout.js when deciding whether to pre-fill form
      // lasts for as long as the tab is open
      sessionStorage.setItem('se', se);
    }

    // see `cexp` fixture in _tda/conftest.py
    let cexp = queryParams.get('cexp')
    if (cexp) {
      currentScope.setTag('cexp', cexp);

      if (cexp === 'products_extremely_slow') {
        PRODUCTS_EXTREMELY_SLOW = true;
      } else if (cexp === 'products_be_error') {
        PRODUCTS_BE_ERROR = true;
      } else if (cexp === 'add_to_cart_js_error') {
        ADD_TO_CART_JS_ERROR = true;
      } else if (cexp === 'checkout_success') {
        CHECKOUT_SUCCESS = true;
      }
    }

    if (queryParams.get('frontendSlowdown') === 'true') {
      console.log('> frontend-only slowdown: true');
      FRONTEND_SLOWDOWN = true;
      currentScope.setTag('frontendSlowdown', true);
    } else {
      console.log('> frontend + backend slowdown');
      currentScope.setTag('frontendSlowdown', false);
    }

    if (queryParams.get('api') === 'join') {
      if (PRODUCTS_EXTREMELY_SLOW || PRODUCTS_BE_ERROR || FRONTEND_SLOWDOWN) {
        throw new Error('?products_api=join can\'t be combined with ?cexp=products_extremely_slow, ?cexp=products_be_error, or ?frontendSlowdown=true');
      }
      PRODUCTS_API = 'products-join';
      currentScope.setTag('api', 'products-join');
    } else {
      PRODUCTS_API = 'products';
      currentScope.setTag('api', 'products');
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

    currentScope.setTag('backendType', backendType);

    let email = null;
    if (queryParams.get('userEmail')) {
      email = queryParams.get('userEmail');
    } else if (se && !se.startsWith('prod-tda-')) {
      email = se + '@example.com';
    } else {
      const letters = 'abcdefghijklmnopqrstuvwxyz';
      email = Array(3)
        .fill()
        .map(() => letters[Math.floor(Math.random() * letters.length)])
        .join('') + '@example.com';
    }
    currentScope.setUser({ email: email });

    let errorBoundary = queryParams.get('error_boundary');
    if (errorBoundary) {
      ERROR_BOUNDARY = errorBoundary;
      currentScope.setTag('error_boundary', errorBoundary);
    }

    // Automatically append `se`, `customerType` and `userEmail` query params to all requests
    // (except for requests to Sentry)
    const nativeFetch = window.fetch;
    window.fetch = async function (...args) {
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
      let res = nativeFetch.apply(window, args);
      if (args[0].includes('/apply-promo-code')) { 
        await new Promise(resolve => setTimeout(resolve, 1000)); // to avoid log lines reordering due to clock drift between FE/BE
      }
      return res;
    };

    // Crasher parses query params sent by /tests for triggering crashes for Release Health
    crasher();
  }

  render() {
    return (
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
                    checkout_success={CHECKOUT_SUCCESS}
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
                element={
                  <Products backend={BACKEND_URL}
                    frontendSlowdown={false}
                    productsApi={PRODUCTS_API}
                    productsExtremelySlow={PRODUCTS_EXTREMELY_SLOW}
                    productsBeError={PRODUCTS_BE_ERROR}
                    addToCartJsError={ADD_TO_CART_JS_ERROR}
                  />
                }
              ></Route>
              <Route
                path="/products-fes" // fes = frontend slowdown (only frontend)
                element={
                  <Products backend={BACKEND_URL} frontendSlowdown={false} />
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
          <Footer backend={BACKEND_URL} errorBoundary={ERROR_BOUNDARY} />
        </BrowserRouter>
      </Provider>
    );
  }
}

// React-router in use here https://reactrouter.com/web/guides/quick-start
ReactDOM.render(<App />, document.getElementById('root'));
