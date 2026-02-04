import * as Sentry from "@sentry/node";
import { config } from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

// Load .env file from the same directory as this file
const __dirname = dirname(fileURLToPath(import.meta.url));
config({ path: join(__dirname, ".env"), override: true });

Sentry.init({
  dsn: process.env.MCP_DSN,
  environment: process.env.MCP_SENTRY_ENVIRONMENT,
  sendDefaultPii: true,
  tracesSampleRate: 1.0,
});
