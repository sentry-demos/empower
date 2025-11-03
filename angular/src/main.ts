import * as Sentry from "@sentry/angular";
import 'zone.js';
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';
import { environment } from './environments/environment';
import {
  determineBackendType,
  determineBackendUrl,
} from './app/utils/backend-router';


// Handle SE parameter from URL (like React)
const queryParams = new URLSearchParams(window.location.search);
const seValue = queryParams.get('se');
if (seValue) {
  sessionStorage.setItem('se', seValue);
}

// Handle backend parameter from URL (like React)
const backendTypeParam = queryParams.get('backend');
const backendType = determineBackendType(backendTypeParam);
const backendUrl = determineBackendUrl(backendType);
console.log(`> backendType: ${backendType} | backendUrl: ${backendUrl}`);

// Handle userEmail parameter (like React)
let email = null;
if (queryParams.get('userEmail')) {
  email = queryParams.get('userEmail');
} else {
  // Generate random email like React
  const array = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'];
  const a = array[Math.floor(Math.random() * array.length)] || 'a';
  const b = array[Math.floor(Math.random() * array.length)] || 'b';
  const c = array[Math.floor(Math.random() * array.length)] || 'c';
  email = a + b + c + '@example.com';
}


// TODO: Temporarily disabled window.fetch override to fix deployment issue
// This was causing the 404 error on staging deployment
// Will re-enable after deployment is fixed
const tracingOrigins = [
    'localhost',
    'empower-plant.com',
    'run.app',
    'appspot.com',
    /^\//,
  ];

// Initialize Sentry with configuration from Angular environment files
Sentry.init({
    dsn: environment.DSN,
    environment: environment.SENTRY_ENVIRONMENT,
    release: environment.RELEASE,
    tracePropagationTargets: tracingOrigins,
    tracesSampleRate: 1,
    replaysSessionSampleRate: 1.0,
    replaysOnErrorSampleRate: 1,
    enableLogs: true,
    debug: true,

    integrations: (defaultIntegrations) => [
        // Filter out the Dedupe integration from the defaults (like React)
        ...defaultIntegrations.filter(integration => integration.name !== "Dedupe"),
        Sentry.browserTracingIntegration(), 
        Sentry.replayIntegration({
            blockAllMedia: false,
            networkDetailAllowUrls: [/.*/],
            unmask: [".sentry-unmask"],
        }),
        Sentry.consoleLoggingIntegration({ 
            levels: ["log", "warn", "error", "info", "debug"] 
        }),
        Sentry.featureFlagsIntegration()
    ],
  
    beforeSend(event) {
        // Get SE value from sessionStorage (like React)
        const se = sessionStorage.getItem('se') || undefined;
        
        // Handle SE tag fingerprinting for errors (like React)
        if (se && event.exception) {
            const is5xxError = event.exception.values && 
                /^5\d{2} - .*$/.test(event.exception.values[0]?.value || '');
            
            if (is5xxError) {
                // Create a separate issue for each SE and RELEASE combination
                const seTdaPrefixRegex = /[^-]+-tda-[^-]+-/;
                let seFingerprint = se;
                let prefix = seTdaPrefixRegex.exec(se);
                
                if (prefix) {
                    // Now that TDA puts platform/browser and test path into SE tag we want to prevent
                    // creating separate issues for those. See https://github.com/sentry-demos/empower/pull/332
                    seFingerprint = prefix[0];
                }
                
                if (se.startsWith('prod-tda-') && environment.RELEASE) {
                    // Release Health
                    event.fingerprint = ['{{ default }}', seFingerprint, environment.RELEASE];
                } else {
                    // SE Testing
                    event.fingerprint = ['{{ default }}', seFingerprint];
                }
            }
        }
        
        // Store last error event ID in sessionStorage (like React)
        if (event.exception && event.event_id) {
            sessionStorage.setItem('lastErrorEventId', event.event_id);
        }
        
        return event;
    }
})

// Set SE parameter in Sentry context (for Angular project)
if (seValue) {
  Sentry.setTag('se', seValue);
}

// Set backendType tag in Sentry context (like React)
Sentry.setTag('backendType', backendType);

// Store values for use in fetch override
const globalSe = seValue;
const globalEmail = email;

// Automatically append SE and email headers to all backend requests (like React)
const nativeFetch = window.fetch;
window.fetch = function (...args) {
  try {
    let url = args[0];
    // Convert to string if it's a Request or URL object
    const urlString = typeof url === 'string' ? url : url.toString();
    
    // Don't add headers to Sentry requests
    let ignore_match = urlString.match(
      /^http[s]:\/\/([^.]+\.ingest\.sentry\.io\/|localhost:9989|127.0.0.1:9989).*/
    );
    
    if (!ignore_match) {
      args[1] = args[1] || {};
      const headers: Record<string, string> = { ...(args[1].headers as Record<string, string>) };
      if (globalSe) headers['se'] = globalSe;
      if (globalEmail) headers['email'] = globalEmail;
      args[1].headers = headers;
    }
    
    return nativeFetch.apply(window, args);
  } catch (error) {
    // If anything goes wrong with the fetch override, fall back to native fetch
    console.warn('Fetch override failed, using native fetch:', error);
    return nativeFetch.apply(window, args);
  }
};

// Track Angular bootstrapping performance
Sentry.startSpan(
  {
    name: "bootstrap-angular-application",
    op: "ui.angular.bootstrap",
  },
  async () => {
    await bootstrapApplication(AppComponent, appConfig)
    .catch(err => {
        console.error('❌ Angular bootstrap error:', err);
        // Also send to Sentry
        Sentry.captureException(err);
    });
  },
);