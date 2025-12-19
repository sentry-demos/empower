import { createApp } from "vue";
import * as Sentry from "@sentry/vue";
import { createPinia } from "pinia";
// import { Debug as DebugIntegration } from "@sentry/integrations";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(createPinia());  
app.use(router);

const RELEASE = import.meta.env.VUE_RELEASE;

const tracingOrigins = [
  'localhost',
  'empower-plant.com',
  'run.app',
  'appspot.com',
  /^\//,
];

Sentry.init({
    app,
    dsn: import.meta.env.VUE_DSN,
    release: RELEASE,
    tracePropagationTargets: tracingOrigins,
    integrations:[
      Sentry.browserTracingIntegration(),
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
    ignoreErrors: ["Missing Translation Key"],
    tracesSampleRate: 1.0,
    autoSessionTracking: true,
    trackComponents: true,
    replaysSessionSampleRate: 1.0,
    replaysOnErrorSampleRate: 1.0,
    profilesSampleRate: 1.0
  });

app.mount("#app");
