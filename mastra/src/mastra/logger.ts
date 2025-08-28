import { createCustomTransport } from "@mastra/core/logger";
import { PinoLogger } from "@mastra/loggers";
import pinoSentry from "pino-sentry-transport";

// Create Sentry stream
const sentryStream = await pinoSentry({
  sentry: {
    dsn: process.env.SENTRY_DSN,
    _experiments: {
      enableLogs: true,
    },
  },
});

// Create custom transport
const customTransport = createCustomTransport(sentryStream);

// Create logger with Sentry transport
export const mastraLogger = new PinoLogger({
  name: "Mastra",
  level: "info",
  transports: { sentry: customTransport },
});
