
'use client'
import React from "react";

import * as Sentry from '@sentry/nextjs';
import { createStore, applyMiddleware, compose } from 'redux';
import logger from 'redux-logger';
import rootReducer from '/src/reducers';
import { Provider } from 'react-redux';
import ScrollToTop from '/src/components/ScrollToTop';
import Nav from '/src/components/Nav';


import '/src/styles/index.css';
import '/src/styles/footer.css';
import '/src/styles/nav.css';
import '/src/styles/products.css';
import '/src/styles/about.css';
import '/src/styles/cart.css';
import '/src/styles/checkout.css';
import '/src/styles/complete.css';
import '/src/styles/product.css';
import Footer from "/src/components/Footer";
import SentryQueryInitializer from "../ui/sentry-query-initializer";


const sentryReduxEnhancer = Sentry.createReduxEnhancer({});

const store = createStore(
  rootReducer,
  compose(applyMiddleware(logger), sentryReduxEnhancer)
);


export default function RootLayout({
  // Layouts must accept a children prop.
  // This will be populated with nested layouts or pages
  children,
}) {
  return (
      <html lang="en">
        <body id="body-container">
        <SentryQueryInitializer />
          <Provider store={store}>
            <ScrollToTop />
            <Nav />
            {children}
          </Provider>
          <Footer />
        </body>
      </html>
  )
}
