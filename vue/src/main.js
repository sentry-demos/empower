import { createApp } from "vue";
import * as Sentry from "@sentry/vue";
import { createPinia } from "pinia";
// import { Debug as DebugIntegration } from "@sentry/integrations";
import { createSentryPiniaPlugin } from "@sentry/vue";

import App from "./App.vue";
import router from "./router";
import { determineBackendType, determineBackendUrl } from "./utils/backendrouter";

const pinia = createPinia();
pinia.use(createSentryPiniaPlugin());
const app = createApp(App);
app.use(pinia);  
app.use(router);

const RELEASE = import.meta.env.RELEASE;

// Backend routing logic
const queryParams = new URLSearchParams(window.location.search);
let backendTypeParam = queryParams.get('backend');
const backendType = determineBackendType(backendTypeParam);
const BACKEND_URL = determineBackendUrl(backendType);

console.log(`> backendType: ${backendType} | backendUrl: ${BACKEND_URL}`);

// Make backend URL available globally
window.BACKEND_URL = BACKEND_URL;
window.BACKEND_TYPE = backendType;

// Global variables for experiment flags
let FRONTEND_SLOWDOWN;
let RAGECLICK;
let PRODUCTS_API;
let PRODUCTS_EXTREMELY_SLOW;
let PRODUCTS_BE_ERROR;
let ADD_TO_CART_JS_ERROR;
let CHECKOUT_SUCCESS;

const tracingOrigins = [
  'localhost',
  'empower-plant.com',
  'run.app',
  'appspot.com',
  /^\//,
];

Sentry.init({
    app,
    dsn: import.meta.env.VITE_APP_DSN,
    release: RELEASE,
    tracePropagationTargets: tracingOrigins,
    integrations:[
      Sentry.vueIntegration({
        tracingOptions:{
          trackComponents: true,
        }
      }),
      Sentry.browserTracingIntegration(),
      Sentry.browserProfilingIntegration(),
      Sentry.replayIntegration({
        blockAllMedia: false,
        networkDetailAllowUrls: ['/checkout', '/products'],
      }),
      Sentry.feedbackIntegration({
        colorScheme: 'system',
      }),
    ],
    beforeSend(event, hint) {
      if (event.exception && event.event_id
        && event.exception.values[0].value.includes("Internal Server Error")
      ) {
        setTimeout(() => {
          Sentry.showReportDialog({ eventId: event.event_id });
        }, 2000);
      }
      return event;
    },
    tracesSampleRate: 1.0,
    autoSessionTracking: true,
    replaysSessionSampleRate: 1.0,
    replaysOnErrorSampleRate: 1.0,
    profilesSampleRate: 1.0,
    enableLogs: true
  });

let currentScope = Sentry.getCurrentScope();

// Set random customer type
const customerType = [
  'medium-plan',
  'large-plan',
  'small-plan',
  'enterprise',
][Math.floor(Math.random() * 4)];
currentScope.setTag('customerType', customerType);

// SE tag tracking for pre-filling forms
let se = queryParams.get('se');
if (se) {
  // Route components (navigation changes) will now have 'se' tag on scope
  currentScope.setTag('se', se);
  // for use in Checkout.js when deciding whether to pre-fill form
  // lasts for as long as the tab is open
  sessionStorage.setItem('se', se);
}

// CEXP experiment tracking
let cexp = queryParams.get('cexp');
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

// Frontend slowdown experiment
if (queryParams.get('frontendSlowdown') === 'true') {
  console.log('> frontend-only slowdown: true');
  FRONTEND_SLOWDOWN = true;
  currentScope.setTag('frontendSlowdown', true);
} else {
  console.log('> frontend + backend slowdown');
  currentScope.setTag('frontendSlowdown', false);
}

// API type experiment
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

// Rage click experiment
if (queryParams.get('rageclick') === 'true') {
  RAGECLICK = true;
}

// User feedback experiment
if (queryParams.get('userFeedback')) {
  sessionStorage.setItem('userFeedback', queryParams.get('userFeedback'));
} else {
  sessionStorage.setItem('userFeedback', 'false');
}
sessionStorage.removeItem('lastErrorEventId');

// Set backend type tag
currentScope.setTag('backendType', backendType);

// User email tracking
let email = null;
if (queryParams.get('userEmail')) {
  email = queryParams.get('userEmail');
} else {
  // making fewer emails so event and user counts for an Issue are not the same
  let array = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z'
  ];
  email = array[Math.floor(Math.random() * array.length)] + '@example.com';
}

// Set user context in Sentry
Sentry.setUser({
  email: email,
  id: email,
});

// Make experiment flags available globally
window.FRONTEND_SLOWDOWN = FRONTEND_SLOWDOWN;
window.RAGECLICK = RAGECLICK;
window.PRODUCTS_API = PRODUCTS_API;
window.PRODUCTS_EXTREMELY_SLOW = PRODUCTS_EXTREMELY_SLOW;
window.PRODUCTS_BE_ERROR = PRODUCTS_BE_ERROR;
window.ADD_TO_CART_JS_ERROR = ADD_TO_CART_JS_ERROR;
window.CHECKOUT_SUCCESS = CHECKOUT_SUCCESS;

app.mount("#app");
