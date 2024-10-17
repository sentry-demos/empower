// // redux/store.js
// import { createStore, applyMiddleware, compose } from 'redux';
// import logger from 'redux-logger';
// import rootReducer from '../reducers'; // Assuming you have a root reducer
// import * as Sentry from '@sentry/react';

// // Create Sentry enhancer
// const sentryReduxEnhancer = Sentry.createReduxEnhancer({});

// // Enable Redux DevTools if available
// const composeEnhancers =
//   typeof window !== 'undefined' && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
//     ? window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
//     : compose;

// // Create the store only once
// const store = createStore(
//   rootReducer,
//   composeEnhancers(applyMiddleware(logger), sentryReduxEnhancer)
// );

// export default store;

import { configureStore } from '@reduxjs/toolkit';
import logger from 'redux-logger';
import rootReducer from '../reducers';
import * as Sentry from '@sentry/react';

const sentryReduxEnhancer = Sentry.createReduxEnhancer({});
export const makeStore = () => {
  return configureStore({
    reducer: rootReducer,
    devTools: true,
    middleware: () => [logger, sentryReduxEnhancer],
  });
};
