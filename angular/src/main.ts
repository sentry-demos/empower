import * as Sentry from "@sentry/angular";
import 'zone.js';
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';
import { environment } from './environments/environment';

// Handle SE parameter from URL (like React)
const queryParams = new URLSearchParams(window.location.search);
const seValue = queryParams.get('se');
if (seValue) {
  Sentry.setTag('se', seValue);
  sessionStorage.setItem('se', seValue);
}

// Initialize Sentry with configuration from Angular environment files
// This is the standard Angular approach (same as React's build-time process.env)
Sentry.init({
    dsn: environment.sentry.dsn,
    environment: environment.sentry.environment,
    release: environment.sentry.release,
    integrations: (defaultIntegrations) => [
        // Filter out the Dedupe integration from the defaults
        ...defaultIntegrations.filter(integration => integration.name !== "Dedupe"),
        Sentry.browserTracingIntegration(), 
        Sentry.replayIntegration({
            // Additional configuration goes in here
            // replaysSessionSampleRate and replaysOnErrorSampleRate is now a top-level SDK option
            blockAllMedia: false,
            // https://docs.sentry.io/platforms/javascript/session-replay/configuration/#network-details
            networkDetailAllowUrls: [/.*/],
            unmask: [".sentry-unmask"],
        }),
        Sentry.consoleLoggingIntegration({ 
            levels: ["log", "warn", "error", "info", "debug"] 
        })
    ],
    tracesSampleRate: 1,
    replaysSessionSampleRate: 1.0,
    replaysOnErrorSampleRate: 1,
    enableLogs: true,
    debug: true, // Enable debug mode to see Sentry logs in console
    beforeSend(event) {
        
        // Get SE value from sessionStorage (simpler approach)
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
                
                if (se.startsWith('prod-tda-')) {
                    // Release Health
                    event.fingerprint = ['{{ default }}', seFingerprint, environment.sentry.release];
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
    },
    beforeSendLog(log) {
        return log;
    }
})


bootstrapApplication(AppComponent, appConfig)
.catch(err => {
    console.error('❌ Angular bootstrap error:', err);
    // Also send to Sentry
    Sentry.captureException(err);
});