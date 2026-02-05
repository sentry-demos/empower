import * as Sentry from "@sentry/node";
import { config } from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

// Load .env file from the app root directory
// Note: After TypeScript compilation, this file is in dist/, but .env is in root
const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = join(__dirname, "..", ".env"); // Go up one level from dist/
config({ path: envPath, override: true });

// Fail fast if required env vars are missing
if (!process.env.MCP_DSN) {
  throw new Error("MCP_DSN environment variable is required");
}
if (!process.env.MCP_SENTRY_ENVIRONMENT) {
  throw new Error("MCP_SENTRY_ENVIRONMENT environment variable is required");
}

Sentry.init({
  dsn: process.env.MCP_DSN,
  environment: process.env.MCP_SENTRY_ENVIRONMENT,
  sendDefaultPii: true,
  tracesSampleRate: 1.0,
});
