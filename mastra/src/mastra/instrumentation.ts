import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { NodeSDK } from '@opentelemetry/sdk-node';
import * as Sentry from '@sentry/node';
import { SentrySpanProcessor } from '@sentry/opentelemetry';



console.log('🚀 Loading Sentry instrumentation...');

// Initialize Sentry with OpenTelemetry integration
Sentry.init({
  dsn: process.env.SENTRY_DSN || "https://8cbcd838f64adaa459e67735368b1ee6@o87286.ingest.us.sentry.io/4508968158429184",

  // Add release tracking
  release: process.env.npm_package_version || '1.0.0',

  // Environment name
  environment: process.env.NODE_ENV || 'development',

  // Configure for better debugging in development
  debug: process.env.NODE_ENV !== 'production',

  // Tracing must be enabled for agent monitoring to work
  tracesSampleRate: 1.0,

  // Enable logging
  enableLogs: true,

  // Send default PII for better debugging
  sendDefaultPii: true,

  // Add integrations
  integrations: [
    // Send console.log, console.warn, and console.error calls as logs to Sentry
    Sentry.consoleLoggingIntegration({
      levels: ["log", "warn", "error"]
    }),
  ],

});

// Debug: Check if Sentry is properly initialized
if (process.env.SENTRY_DSN) {
  console.log('✅ Sentry initialized with DSN:', process.env.SENTRY_DSN.substring(0, 20) + '...');
} else {
  console.log('✅ Sentry initialized with default DSN');
}

// // Create the OpenTelemetry SDK with Sentry integration
// const sdk = new NodeSDK({
//   // Add auto-instrumentations for Node.js
//   instrumentations: [getNodeAutoInstrumentations()],

//   // Add Sentry span processor to send spans to Sentry
//   spanProcessors: [new SentrySpanProcessor()],
// });

// // Start the SDK
// sdk.start();

// console.log('🔧 OpenTelemetry SDK started');

// export default Sentry;

