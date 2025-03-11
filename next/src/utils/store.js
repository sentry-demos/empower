
import { createStore, compose, applyMiddleware } from 'redux';
import logger from 'redux-logger';
import * as Sentry from '@sentry/nextjs';
import rootReducer from '@/src/reducers';

const sentryReduxEnhancer = Sentry.createReduxEnhancer({});

// Create store outside of component
export const store = createStore(
  rootReducer,
  compose(applyMiddleware(logger), sentryReduxEnhancer)
);