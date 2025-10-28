require("dotenv").config();
const {
  NodeClient,
  defaultStackParser,
  getDefaultIntegrations,
  makeNodeTransport,
  Scope,
  knexIntegration,
} = require("@sentry/node");

// Environment variables
const dsn = process.env.EXPRESS_DSN;
const release = process.env.EXPRESS_RELEASE;
const environment = process.env.EXPRESS_ENVIRONMENT;

// Filter integrations that use the global variable
const integrations = getDefaultIntegrations({}).filter((defaultIntegration) => {
  return !["BrowserApiErrors", "Breadcrumbs", "GlobalHandlers"].includes(
    defaultIntegration.name
  );
});

// Add knex integration
integrations.push(knexIntegration());

// Create Sentry client manually
const client = new NodeClient({
  dsn: dsn,
  environment: environment,
  release: release,
  transport: makeNodeTransport,
  stackParser: defaultStackParser,
  integrations: integrations,
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
  enableTracing: true,
  debug: true,
  tracesSampler: (samplingContext) => {
    // sample out transactions from http OPTIONS requests hitting endpoints
    const request = samplingContext.request;
    if (request && request.method === "OPTIONS") {
      return 0.0;
    } else {
      return 1.0;
    }
  },
  beforeSend: (event, hint) => {
    // Mark all errors as unhandled (handled: false)
    if (event.exception && event.exception.values) {
      event.exception.values.forEach((exception) => {
        if (exception.mechanism) {
          exception.mechanism.handled = false;
        } else {
          exception.mechanism = { handled: false, type: "generic" };
        }
      });
    }
    return event;
  },
});

const scope = new Scope();
scope.setClient(client);
client.init(); // initializing has to be done after setting the client on the scope

console.log("attempting to record node layer error...");
scope.captureException(new Error("manually captured node layer error"));

console.log("> Sentry initialized (manual)");

console.log("> DSN", dsn);
console.log("> RELEASE", "9.0.0");
console.log("> ENVIRONMENT", environment);
