'use client'

import * as Sentry from '@sentry/nextjs';
import { createStore, applyMiddleware, compose } from 'redux';
import logger from 'redux-logger';
import rootReducer from '/src/reducers';

import Footer from "/src/components/Footer";
import { Provider } from 'react-redux';
import ScrollToTop from '/src/components/ScrollToTop';
import Nav from '/src/components/Nav';

const sentryReduxEnhancer = Sentry.createReduxEnhancer({});

const store = createStore(
  rootReducer,
  compose(applyMiddleware(logger), sentryReduxEnhancer)
);


export default function HomeContent({children}) {
  return (
    <>
      <Provider store={store}>
        <ScrollToTop />
        <Nav />
        {children}
      </Provider>
      <Footer />
    </>
  )
}