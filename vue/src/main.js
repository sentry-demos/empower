import { createApp } from "vue";
import * as Sentry from "@sentry/vue";
import { createPinia } from "pinia";
// import { Debug as DebugIntegration } from "@sentry/integrations";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(createPinia());  
app.use(router);

const RELEASE = import.meta.env.VITE_RELEASE;

Sentry.init({
    app,
    dsn: import.meta.env.VITE_APP_DSN,
    release: RELEASE,
    integrations: [
      new Sentry.BrowserTracing({
        routingInstrumentation: Sentry.vueRouterInstrumentation(router),
        tracingOrigins: ["localhost", "my-site-url.com", /^\//],
      }),
    //   new DebugIntegration(
    //     {
    //       // trigger DevTools debugger instead of using console.log
    //       debugger: true,
    
    //       // stringify event before passing it to console.log
    //       stringify: true,
    //     }
    //   )
    new Sentry.Replay(),
    ],
    // Set tracesSampleRate to 1.0 to capture 100%
    // of transactions for performance monitoring.
    // We recommend adjusting this value in production
    tracesSampleRate: 1.0,

    replaysOnErrorSampleRate: 1.0,
    replaysSessionSampleRate: 1.0,
    autoSessionTracking: true,
    trackComponents: true,
  });

app.mount("#app");
