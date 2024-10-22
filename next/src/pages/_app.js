import React from 'react';
import App from 'next/app';

import '../styles/index.css';
import '../styles/footer.css';
import '../styles/nav.css';
import '../styles/products.css';
import '../styles/about.css';
import '../styles/cart.css';
import '../styles/checkout.css';
import '../styles/complete.css';
import '../styles/product.css';
import '../styles/employee.css';

import 'react-loader-spinner/dist/loader/css/react-spinner-loader.css';
import * as Sentry from '@sentry/nextjs';

import { crasher } from '../utils/errors';
import {
  determineBackendType,
  determineBackendUrl,
} from '../utils/backendrouter';

import { Provider } from 'react-redux';
import { createStore, applyMiddleware, compose } from 'redux';
import logger from 'redux-logger';
import rootReducer from '../reducers';

import ScrollToTop from '../components/ScrollToTop';
import Footer from '../components/Footer';
import Nav from '../components/Nav';

let BACKEND_URL;
const RELEASE = process.env.NEXT_PUBLIC_RELEASE;

console.log('RELEASE', RELEASE);

function initSentry(environment) {
  Sentry.init({
    release: RELEASE,
    environment: environment,
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
}

const sentryReduxEnhancer = Sentry.createReduxEnhancer({});

const store = createStore(
  rootReducer,
  compose(applyMiddleware(logger), sentryReduxEnhancer)
);

class MyApp extends App {
  constructor(props) {
    super(props);
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
  }

  static async getInitialProps(appContext) {
    // Call the parent class's getInitialProps to get pageProps
    console.log('in get initial props');

    const appProps = await App.getInitialProps(appContext);
    // Get hostname from the request headers (only available server-side)
    if (appContext.ctx.req) {
      const host = appContext.ctx.req.headers.host;
      const { query } = appContext.ctx;
      const environment = host.includes('localhost') ? 'test' : 'production';

      // Initialize Sentry here with the detected host
      initSentry(environment);
      // Pass the globalHost to the app as well as the page props
      return {
        ...appProps,
        pageProps: {
          ...appProps.pageProps,
          environment,
          query,
        },
      };
    }
    return { ...appProps };
  }

  componentDidMount() {
    console.log('componentDidMount called');
    const { query } = this.props.pageProps;
    const backendType = determineBackendType(query.backend);
    BACKEND_URL = determineBackendUrl(backendType);
    console.log(`> backendType: ${backendType} | backendUrl: ${BACKEND_URL}`);

    // These also get passed via request headers (see window.fetch below)

    // NOTE: because the demo extracts tags from the scope in order to pass them
    // as headers to the backend, we need to make sure we are calling `setTag()`
    // on the current scope. We don't want to call Sentry.setTag() as is usually
    // recommended (https://docs.sentry.io/platforms/javascript/enriching-events/scopes/#isolation-scope),
    // because that would set the tag on the isolation scope, and make it inaccessible
    // when it's time to set the headers.
    let currentScope = Sentry.getCurrentScope();

    const customerType = [
      'medium-plan',
      'large-plan',
      'small-plan',
      'enterprise',
    ][Math.floor(Math.random() * 4)];
    currentScope.setTag('customerType', customerType);

    if (query.se) {
      // Route components (navigation changes) will now have 'se' tag on scope
      console.log('> src/index.js se', query.se);
      currentScope.setTag('se', query.se);
      // for use in Checkout.js when deciding whether to pre-fill form
      // lasts for as long as the tab is open
      sessionStorage.setItem('se', query.se);
    }

    if (query.frontendSlowdown === 'true') {
      console.log('> frontend-only slowdown: true');
      currentScope.setTag('frontendSlowdown', true);
    } else {
      console.log('> frontend + backend slowdown');
      currentScope.setTag('frontendSlowdown', false);
    }

    if (query.userFeedback) {
      sessionStorage.setItem('userFeedback', query.userFeedback);
    } else {
      sessionStorage.setItem('userFeedback', 'false');
    }
    sessionStorage.removeItem('lastErrorEventId');

    currentScope.setTag('backendType', backendType);

    let email = null;
    if (query.userEmail) {
      email = query.userEmail;
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
    currentScope.setUser({ email: email });

    // TODO: Figure out why this is forcing a rerender on initial "Browse products" button click, or add tags to idnvidual network calls
    // // Automatically append `se`, `customerType` and `userEmail` query params to all requests
    // // (except for requests to Sentry)
    // const nativeFetch = window.fetch;
    // window.fetch = function (...args) {
    //   let url = args[0];
    //   // When TDA is run in 'mock' mode inside Docker mini-relay will be ingesting on port 9989, see:
    //   // https://github.com/sentry-demos/empower/blob/79bed0b78fb3d40dff30411ef26c31dc7d4838dc/mini-relay/Dockerfile#L9
    //   let ignore_match = url.match(
    //     /^http[s]:\/\/([^.]+\.ingest\.sentry\.io\/|localhost:9989|127.0.0.1:9989).*/
    //   );
    //   if (!ignore_match) {
    //     Sentry.withScope(function (scope) {
    //       let se, customerType, email;å
    //       [se, customerType] = [scope._tags.se, scope._tags.customerType];
    //       email = scope._user.email;
    //       args[1].headers = { ...args[1].headers, se, customerType, email };
    //     });
    //   }
    //   return nativeFetch.apply(window, args);
    // };

    // Crasher parses query params sent by /tests for triggering crashes for Release Health
    crasher();
  }

  render() {
    const { Component, pageProps } = this.props;

    return (
      <Provider store={store}>
        <ScrollToTop />
        <Nav />
        <div id="body-container">
          <Component {...pageProps} /> {/* Render the current page */}
        </div>
        <Footer />
      </Provider>
    );
  }

  // render() {
  //   return (
  //     <Provider store={store}>
  //       <BrowserRouter history={history}>
  //         <ScrollToTop />
  //         <Nav frontendSlowdown={FRONTEND_SLOWDOWN} />
  //         <div id="body-container">
  //           <SentryRoutes>
  //             <Route
  //               path="/"
  //               element={
  //                 <Home
  //                   backend={BACKEND_URL}
  //                   frontendSlowdown={FRONTEND_SLOWDOWN}
  //                 />
  //               }
  //             ></Route>
  //             <Route
  //               path="/about"
  //               element={<About backend={BACKEND_URL} history={history} />}
  //             ></Route>
  //             <Route path="/cart" element={<Cart />} />
  //             <Route
  //               path="/checkout"
  //               element={
  //                 <Checkout
  //                   backend={BACKEND_URL}
  //                   rageclick={RAGECLICK}
  //                   history={history}
  //                 />
  //               }
  //             ></Route>
  //             <Route path="/complete" element={<Complete />} />
  //             <Route path="/error" element={<CompleteError />} />
  //             <Route path="/employee/:id" element={<Employee />}></Route>
  //             <Route path="/product/:id" element={<Product />}></Route>
  //             <Route
  //               path="/products"
  //               element={<Products backend={BACKEND_URL} />}
  //             ></Route>
  //             <Route
  //               path="/products-fes" // fes = frontend slowdown (only frontend)
  //               element={
  //                 <Products backend={BACKEND_URL} frontendSlowdown={true} />
  //               }
  //             ></Route>
  //             <Route
  //               path="/nplusone"
  //               element={<Nplusone backend={BACKEND_URL} />}
  //             />
  //             <Route
  //               path="/products-join"
  //               element={<ProductsJoin backend={BACKEND_URL} />}
  //             ></Route>
  //             <Route path="*" element={<NotFound />} />
  //           </SentryRoutes>
  //         </div>
  //         <Footer />
  //       </BrowserRouter>
  //     </Provider>
  //   );
  // }
}

export default MyApp;
