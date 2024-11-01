'use client'

import * as Sentry from '@sentry/nextjs';
import { createStore, applyMiddleware, compose } from 'redux';
import logger from 'redux-logger';
import rootReducer from '@/src/reducers';

import Footer from "@/src/ui/Footer";
import { Provider } from 'react-redux';
import ScrollToTop from '@/src/ui/ScrollToTop';
import Nav from '@/src/ui/Nav';

import '@/src/styles/index.css';
import '@/src/styles/footer.css';
import '@/src/styles/nav.css';
import '@/src/styles/products.css';
import '@/src/styles/about.css';
import '@/src/styles/cart.css';
import '@/src/styles/checkout.css';
import '@/src/styles/complete.css';
import '@/src/styles/product.css';


const sentryReduxEnhancer = Sentry.createReduxEnhancer({});

const store = createStore(
  rootReducer,
  compose(applyMiddleware(logger), sentryReduxEnhancer)
);


export default function HomeContent({ children }) {
  return (
    <>
      <Provider store={store}>
        <ScrollToTop />
        <Nav />
        <div id="body-container">
          {children}
        </div>
      </Provider>
      <Footer />
    </>
  )
}
