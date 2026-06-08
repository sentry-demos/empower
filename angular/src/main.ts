import * as Sentry from "@sentry/angular";
import 'zone.js';
import { bootstrapApplication } from '@angular/platform-browser';
import { Router } from '@angular/router';
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
} else if (seValue && !seValue.startsWith('prod-tda-')) {
  // Use SE value as email prefix if available (like React)
  email = seValue + '@example.com';
} else {
  // Generate random email like React
  const array = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'];
  const a = array[Math.floor(Math.random() * array.length)] || 'a';
  const b = array[Math.floor(Math.random() * array.length)] || 'b';
  const c = array[Math.floor(Math.random() * array.length)] || 'c';
  email = a + b + c + '@example.com';
}

// Generate random customerType (like React)
const customerType = [
  'medium-plan',
  'large-plan',
  'small-plan',
  'enterprise',
][Math.floor(Math.random() * 4)] || 'medium-plan';

sessionStorage.setItem('customerType', customerType);

// Handle cexp parameter (like React)
const cexp = queryParams.get('cexp');
if (cexp) {
  sessionStorage.setItem('cexp', cexp);
}

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
    propagateTraceparent: true,
    tracesSampleRate: 1,
    profilesSampleRate: 1.0,
    replaysSessionSampleRate: 1.0,
    replaysOnErrorSampleRate: 1,
    enableLogs: true,
    debug: true,
    beforeSendLog: (log: any) => {
        const tags = Sentry.getIsolationScope().getScopeData().tags;
        if ('user.email' in tags) {
            log.attributes = log.attributes || {};
            log.attributes['user.email'] = tags['user.email'];
        }
        return log;
    },

    integrations: (defaultIntegrations) => [
        ...defaultIntegrations.filter(integration => integration.name !== "Dedupe"),
        Sentry.feedbackIntegration({
            colorScheme: 'system',
        }),
        Sentry.browserProfilingIntegration(),
        Sentry.browserTracingIntegration({
            instrumentNavigation: true,
            instrumentPageLoad: true,
        }), 
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
        const se = sessionStorage.getItem('se') || undefined;

        const is5xxError = event.exception &&
            event.exception.values &&
            /^5\d{2} - .*$/.test(event.exception.values[0]?.value || '');

        if (se && is5xxError) {
            const seTdaPrefixRegex = /[^-]+-tda-[^-]+-/;
            let seFingerprint = se;
            const prefix = seTdaPrefixRegex.exec(se);

            if (prefix) {
                seFingerprint = prefix[0];
            }

            if (se.startsWith('prod-tda-') && environment.RELEASE) {
                event.fingerprint = ['{{ default }}', seFingerprint, environment.RELEASE];
            } else {
                event.fingerprint = ['{{ default }}', seFingerprint];
            }
        } else {
            event.fingerprint = ['{{ default }}'];
        }

        if (is5xxError) {
            event.fingerprint = event.fingerprint || ['{{ default }}'];
            event.fingerprint.push(backendType);
        }

        if (event.exception && event.event_id) {
            sessionStorage.setItem('lastErrorEventId', event.event_id);
        }

        return event;
    }
})

const currentScope = Sentry.getCurrentScope();

if (seValue) {
  currentScope.setTag('se', seValue);
}

currentScope.setTag('backendType', backendType);
currentScope.setTag('customerType', customerType);

if (cexp) {
  currentScope.setTag('cexp', cexp);
}

const metricScopeAttrs: Record<string, string> = { backendType };
if (cexp) {
  metricScopeAttrs['cexp'] = cexp;
}
(Sentry.getGlobalScope() as any).setAttributes(metricScopeAttrs);

Sentry.setUser({ email: email ?? undefined });
currentScope.setTag('user.email', email ?? '');

const globalSe = seValue;
const globalEmail = email;
const globalCustomerType = customerType;
const globalCexp = cexp;

const nativeFetch = window.fetch;
window.fetch = function (...args: any[]) {
  try {
    const url = args[0];
    const urlString = typeof url === 'string' ? url : url.toString();

    const ignore_match = urlString.match(
      /^http[s]:\/\/([^.]+\.ingest\.sentry\.io\/|localhost:9989|127.0.0.1:9989).*/
    );

    if (!ignore_match) {
      args[1] = args[1] || {};
      const headers: Record<string, string> = { ...(args[1].headers as Record<string, string>) };
      if (globalSe) headers['se'] = globalSe;
      if (globalCustomerType) headers['customerType'] = globalCustomerType;
      if (globalEmail) headers['email'] = globalEmail;
      if (globalCexp) headers['cexp'] = globalCexp;
      args[1].headers = headers;
    }

    let res = nativeFetch.apply(window, args as any);
    if (urlString.includes('/apply-promo-code')) {
      res = res.then((response: Response) =>
        new Promise<Response>(resolve => setTimeout(() => resolve(response), 1500))
      );
    }
    return res;
  } catch (error) {
    console.warn('Fetch override failed, using native fetch:', error);
    return nativeFetch.apply(window, args as any);
  }
} as typeof window.fetch;

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