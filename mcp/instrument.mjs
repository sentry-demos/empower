import * as Sentry from "@sentry/node";

Sentry.init({
  dsn: "https://e9eb3b0ff1e7a727244e1abf8e9574ab@sandbox-mirror.sentry.gg/1",
  sendDefaultPii: true,
  tracesSampleRate: 1.0,
});
