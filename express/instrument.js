
require("dotenv").config();
const Sentry = require("@sentry/node");

// Environment variables
const dsn = process.env.EXPRESS_APP_DSN;
const release = process.env.RELEASE;
const environment = process.env.EXPRESS_ENV;

// Initialize Sentry
Sentry.init({
  dsn: dsn,
  environment: environment,
  release: release,
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
  enableTracing: true,
  debug:true, 
  integrations: [Sentry.knexIntegration()],
  tracesSampler: (samplingContext) => {
    // sample out transactions from http OPTIONS requests hitting endpoints
    const request = samplingContext.request;
    if (request && request.method === "OPTIONS") {
      return 0.0;
    } else {
      return 1.0;
    }
  },
});

console.log("> Sentry initialized");

console.log("> DSN", dsn);
console.log("> RELEASE", release);
console.log("> ENVIRONMENT", environment);